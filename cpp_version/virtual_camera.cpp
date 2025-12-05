/*
 * Windows 虚拟摄像头 - C++ DirectShow 实现
 * 使用 DirectShow + OpenCV 实现虚拟摄像头
 */

#include <windows.h>
#include <dshow.h>
#include <streams.h>
#include <opencv2/opencv.hpp>
#include <iostream>
#include <thread>
#include <atomic>

#pragma comment(lib, "strmiids.lib")
#pragma comment(lib, "strmbase.lib")

using namespace cv;
using namespace std;

// 虚拟摄像头源过滤器类
class VirtualCameraPin : public CSourceStream {
private:
    VideoCapture cap;
    Mat currentFrame;
    int frameRate;
    int frameWidth;
    int frameHeight;
    REFERENCE_TIME rtFrameLength;
    atomic<bool> shouldLoop;
    string videoPath;

public:
    VirtualCameraPin(HRESULT* phr, CSource* pFilter, const string& path, int fps = 30)
        : CSourceStream(NAME("Virtual Camera Pin"), phr, pFilter, L"Output"),
          videoPath(path), frameRate(fps), frameWidth(1280), frameHeight(720),
          shouldLoop(true) {
        
        // 计算帧间隔时间 (100纳秒单位)
        rtFrameLength = UNITS / frameRate;
        
        // 打开视频文件
        cap.open(videoPath);
        if (!cap.isOpened()) {
            *phr = E_FAIL;
            return;
        }
        
        // 获取视频信息
        frameWidth = (int)cap.get(CAP_PROP_FRAME_WIDTH);
        frameHeight = (int)cap.get(CAP_PROP_FRAME_HEIGHT);
        
        cout << "视频已加载: " << videoPath << endl;
        cout << "分辨率: " << frameWidth << "x" << frameHeight << endl;
        cout << "帧率: " << frameRate << " FPS" << endl;
    }

    ~VirtualCameraPin() {
        if (cap.isOpened()) {
            cap.release();
        }
    }

    // 设置媒体类型
    HRESULT GetMediaType(CMediaType* pMediaType) {
        CAutoLock cAutoLock(m_pFilter->pStateLock());
        
        VIDEOINFOHEADER* pvi = (VIDEOINFOHEADER*)pMediaType->AllocFormatBuffer(sizeof(VIDEOINFOHEADER));
        if (pvi == NULL) return E_OUTOFMEMORY;

        ZeroMemory(pvi, sizeof(VIDEOINFOHEADER));
        
        pvi->bmiHeader.biSize = sizeof(BITMAPINFOHEADER);
        pvi->bmiHeader.biWidth = frameWidth;
        pvi->bmiHeader.biHeight = frameHeight;
        pvi->bmiHeader.biPlanes = 1;
        pvi->bmiHeader.biBitCount = 24;
        pvi->bmiHeader.biCompression = BI_RGB;
        pvi->bmiHeader.biSizeImage = GetBitmapSize(&pvi->bmiHeader);
        pvi->AvgTimePerFrame = rtFrameLength;

        SetRectEmpty(&(pvi->rcSource));
        SetRectEmpty(&(pvi->rcTarget));

        pMediaType->SetType(&MEDIATYPE_Video);
        pMediaType->SetFormatType(&FORMAT_VideoInfo);
        pMediaType->SetTemporalCompression(FALSE);
        pMediaType->SetSubtype(&MEDIASUBTYPE_RGB24);
        pMediaType->SetSampleSize(pvi->bmiHeader.biSizeImage);

        return S_OK;
    }

    // 填充视频帧数据
    HRESULT FillBuffer(IMediaSample* pSample) {
        BYTE* pData;
        long cbData;

        pSample->GetPointer(&pData);
        cbData = pSample->GetSize();

        // 读取视频帧
        bool ret = cap.read(currentFrame);
        
        // 如果视频结束，循环播放
        if (!ret) {
            cap.set(CAP_PROP_POS_FRAMES, 0);
            ret = cap.read(currentFrame);
            
            if (!ret) {
                return E_FAIL;
            }
            
            cout << "视频循环播放" << endl;
        }

        // 调整帧大小
        if (currentFrame.cols != frameWidth || currentFrame.rows != frameHeight) {
            resize(currentFrame, currentFrame, Size(frameWidth, frameHeight));
        }

        // 转换为RGB24格式（DirectShow使用BGR，但上下颠倒）
        Mat flippedFrame;
        flip(currentFrame, flippedFrame, 0);  // 垂直翻转

        // 复制数据到sample
        int imageSize = frameWidth * frameHeight * 3;
        if (cbData < imageSize) {
            return E_FAIL;
        }

        memcpy(pData, flippedFrame.data, imageSize);
        pSample->SetActualDataLength(imageSize);
        pSample->SetSyncPoint(TRUE);

        return S_OK;
    }

    // 设置帧率时间戳
    HRESULT DecideBufferSize(IMemAllocator* pAlloc, ALLOCATOR_PROPERTIES* pRequest) {
        CAutoLock cAutoLock(m_pFilter->pStateLock());
        
        HRESULT hr;
        VIDEOINFOHEADER* pvi = (VIDEOINFOHEADER*)m_mt.Format();

        if (pRequest->cBuffers == 0) {
            pRequest->cBuffers = 2;
        }
        pRequest->cbBuffer = pvi->bmiHeader.biSizeImage;

        ALLOCATOR_PROPERTIES Actual;
        hr = pAlloc->SetProperties(pRequest, &Actual);
        if (FAILED(hr)) {
            return hr;
        }

        if (Actual.cbBuffer < pRequest->cbBuffer) {
            return E_FAIL;
        }

        return S_OK;
    }
};

// 虚拟摄像头源过滤器
class VirtualCameraSource : public CSource {
public:
    static CUnknown* WINAPI CreateInstance(LPUNKNOWN pUnk, HRESULT* phr) {
        VirtualCameraSource* pNewFilter = new VirtualCameraSource(pUnk, phr);
        if (phr) {
            if (pNewFilter == NULL) {
                *phr = E_OUTOFMEMORY;
            } else {
                *phr = S_OK;
            }
        }
        return pNewFilter;
    }

private:
    VirtualCameraSource(LPUNKNOWN pUnk, HRESULT* phr)
        : CSource(NAME("Virtual Camera Source"), pUnk, CLSID_NULL) {
        // Pin会在这里被创建
    }
};

// 主程序
int main(int argc, char* argv[]) {
    cout << "========================================" << endl;
    cout << "Windows 虚拟摄像头 - C++ 版本" << endl;
    cout << "========================================" << endl << endl;

    if (argc < 2) {
        cout << "用法: " << argv[0] << " <视频文件路径> [帧率]" << endl;
        cout << "示例: " << argv[0] << " video.mp4 30" << endl;
        return 1;
    }

    string videoPath = argv[1];
    int fps = (argc >= 3) ? atoi(argv[2]) : 30;

    cout << "视频文件: " << videoPath << endl;
    cout << "目标帧率: " << fps << " FPS" << endl << endl;

    // 初始化COM
    CoInitialize(NULL);

    // 创建DirectShow图形
    IGraphBuilder* pGraph = NULL;
    IMediaControl* pControl = NULL;
    IMediaEvent* pEvent = NULL;

    HRESULT hr = CoCreateInstance(CLSID_FilterGraph, NULL, CLSCTX_INPROC_SERVER,
                                   IID_IGraphBuilder, (void**)&pGraph);
    if (FAILED(hr)) {
        cout << "错误: 无法创建FilterGraph" << endl;
        CoUninitialize();
        return 1;
    }

    pGraph->QueryInterface(IID_IMediaControl, (void**)&pControl);
    pGraph->QueryInterface(IID_IMediaEvent, (void**)&pEvent);

    // 这里需要注册虚拟摄像头过滤器到系统
    // 实际实现需要更多的DirectShow基础设施代码

    cout << "按任意键停止..." << endl;
    
    // 运行图形
    pControl->Run();

    // 等待用户输入
    cin.get();

    // 清理
    pControl->Stop();
    pEvent->Release();
    pControl->Release();
    pGraph->Release();
    CoUninitialize();

    cout << "虚拟摄像头已停止" << endl;
    return 0;
}


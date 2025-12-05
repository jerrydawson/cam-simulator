cmake_minimum_required(VERSION 3.10)
project(VirtualCamera)

set(CMAKE_CXX_STANDARD 17)

# 查找 OpenCV
find_package(OpenCV REQUIRED)

# Windows DirectShow 库路径
if(WIN32)
    # DirectShow SDK 路径（需要手动指定）
    set(DSHOW_SDK_PATH "C:/Program Files/Microsoft SDKs/Windows/v7.1/Samples/multimedia/directshow")
    
    include_directories(
        ${OpenCV_INCLUDE_DIRS}
        ${DSHOW_SDK_PATH}/BaseClasses
    )
    
    # 添加可执行文件
    add_executable(virtual_camera 
        virtual_camera.cpp
    )
    
    # 链接库
    target_link_libraries(virtual_camera 
        ${OpenCV_LIBS}
        strmiids
        ole32
        oleaut32
        uuid
        winmm
    )
    
    # BaseClasses 需要单独编译
    # 这里假设已经编译好了 strmbase.lib
    
else()
    message(FATAL_ERROR "This project only supports Windows")
endif()


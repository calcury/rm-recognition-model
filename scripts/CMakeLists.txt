cmake_minimum_required(VERSION 3.10)
project(video_grayscale_converter)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 可执行文件输出到 scripts/build/
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/build)

# 查找并链接OpenCV
find_package(OpenCV REQUIRED)
include_directories(${OpenCV_INCLUDE_DIRS})

add_executable(video_to_grayscale video_to_grayscale.cpp)
target_link_libraries(video_to_grayscale ${OpenCV_LIBS})
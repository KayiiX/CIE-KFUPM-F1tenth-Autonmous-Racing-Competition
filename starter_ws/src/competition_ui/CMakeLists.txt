cmake_minimum_required(VERSION 3.8)
project(competition_ui)

if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()

find_package(ament_cmake_ros REQUIRED)
find_package(pluginlib REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rviz_common REQUIRED)
find_package(std_msgs REQUIRED)
find_package(Qt5 REQUIRED COMPONENTS Widgets)

set(CMAKE_AUTOMOC ON)
qt5_wrap_cpp(MOC_FILES
  include/competition_ui/race_dashboard_panel.hpp
)

add_library(race_dashboard_panel SHARED
  src/race_dashboard_panel.cpp
  ${MOC_FILES}
)

target_include_directories(race_dashboard_panel PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)

ament_target_dependencies(race_dashboard_panel
  pluginlib
  rclcpp
  rviz_common
  std_msgs
)
target_link_libraries(race_dashboard_panel Qt5::Widgets)

install(
  TARGETS race_dashboard_panel
  EXPORT export_competition_ui
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin
)
install(DIRECTORY include/ DESTINATION include)
install(FILES rviz_common_plugins.xml DESTINATION share/${PROJECT_NAME})

ament_export_include_directories(include)
ament_export_targets(export_competition_ui)
pluginlib_export_plugin_description_file(rviz_common rviz_common_plugins.xml)

ament_package()
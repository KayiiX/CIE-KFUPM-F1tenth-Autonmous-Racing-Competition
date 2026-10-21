#ifndef COMPETITION_UI__RACE_DASHBOARD_PANEL_HPP_
#define COMPETITION_UI__RACE_DASHBOARD_PANEL_HPP_

#include <memory>
#include <string>
#include <vector>

#include <QLabel>
#include <QString>

#include <rclcpp/rclcpp.hpp>
#include <rviz_common/panel.hpp>
#include <rviz_common/ros_integration/ros_node_abstraction_iface.hpp>
#include <std_msgs/msg/float32.hpp>
#include <std_msgs/msg/float32_multi_array.hpp>
#include <std_msgs/msg/int32.hpp>
#include <std_msgs/msg/string.hpp>

namespace competition_ui
{

class RaceDashboardPanel : public rviz_common::Panel
{
  Q_OBJECT

public:
  explicit RaceDashboardPanel(QWidget * parent = nullptr);
  ~RaceDashboardPanel() override;

  void onInitialize() override;

private:
  static QString formatTime(float seconds);
  void refreshLapDisplay();
  void updateStatus(const std::string & status);
  void updateCurrent(float seconds);
  void updateLast(float seconds);
  void updateBest(float seconds);
  void updateLapCount(int count);
  void updateCollisionCount(int count);
  void updateHistory(const std::vector<float> & history);

  std::shared_ptr<rviz_common::ros_integration::RosNodeAbstractionIface> node_ptr_;
  rclcpp::Subscription<std_msgs::msg::String>::SharedPtr status_sub_;
  rclcpp::Subscription<std_msgs::msg::Float32>::SharedPtr current_sub_;
  rclcpp::Subscription<std_msgs::msg::Float32>::SharedPtr last_sub_;
  rclcpp::Subscription<std_msgs::msg::Float32>::SharedPtr best_sub_;
  rclcpp::Subscription<std_msgs::msg::Int32>::SharedPtr count_sub_;
  rclcpp::Subscription<std_msgs::msg::Int32>::SharedPtr collision_count_sub_;
  rclcpp::Subscription<std_msgs::msg::Float32MultiArray>::SharedPtr history_sub_;

  QLabel * status_value_;
  QLabel * lap_value_;
  QLabel * lap_subtitle_;
  QLabel * current_value_;
  QLabel * last_value_;
  QLabel * best_value_;
  QLabel * collision_value_;
  QLabel * history_value_;

  std::string status_{"WAITING_FOR_ODOMETRY"};
  int completed_laps_{0};
};

}  // namespace competition_ui

#endif  // COMPETITION_UI__RACE_DASHBOARD_PANEL_HPP_

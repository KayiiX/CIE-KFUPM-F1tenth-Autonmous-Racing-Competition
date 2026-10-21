#include "competition_ui/race_dashboard_panel.hpp"

#include <algorithm>
#include <functional>

#include <QChar>
#include <QFrame>
#include <QGridLayout>
#include <QMetaObject>
#include <QSizePolicy>
#include <QStyle>
#include <QVBoxLayout>

#include <pluginlib/class_list_macros.hpp>
#include <rviz_common/display_context.hpp>

namespace competition_ui
{

RaceDashboardPanel::RaceDashboardPanel(QWidget * parent)
: Panel(parent)
{
  setMinimumWidth(285);
  setObjectName("raceDashboard");

  auto * root = new QVBoxLayout(this);
  root->setContentsMargins(14, 14, 14, 14);
  root->setSpacing(10);

  auto * series = new QLabel("CIE · KFUPM");
  series->setObjectName("series");
  auto * title = new QLabel("F1TENTH\nRACE CONTROL");
  title->setObjectName("title");
  root->addWidget(series);
  root->addWidget(title);

  auto * red_line = new QFrame();
  red_line->setObjectName("redLine");
  red_line->setFixedHeight(4);
  root->addWidget(red_line);

  auto * status_caption = new QLabel("SESSION STATUS");
  status_caption->setObjectName("caption");
  status_value_ = new QLabel("WAITING");
  status_value_->setObjectName("statusWaiting");
  status_value_->setAlignment(Qt::AlignCenter);
  root->addWidget(status_caption);
  root->addWidget(status_value_);

  auto * lap_frame = new QFrame();
  lap_frame->setObjectName("lapFrame");
  auto * lap_layout = new QVBoxLayout(lap_frame);
  lap_layout->setContentsMargins(12, 10, 12, 10);
  auto * lap_caption = new QLabel("LAP");
  lap_caption->setObjectName("caption");
  lap_value_ = new QLabel("--");
  lap_value_->setObjectName("lapValue");
  lap_value_->setAlignment(Qt::AlignCenter);
  lap_subtitle_ = new QLabel("OUT LAP");
  lap_subtitle_->setObjectName("lapSubtitle");
  lap_subtitle_->setAlignment(Qt::AlignCenter);
  lap_layout->addWidget(lap_caption);
  lap_layout->addWidget(lap_value_);
  lap_layout->addWidget(lap_subtitle_);
  root->addWidget(lap_frame);

  auto * current_caption = new QLabel("CURRENT LAP");
  current_caption->setObjectName("caption");
  current_value_ = new QLabel("--:--.---");
  current_value_->setObjectName("currentTime");
  current_value_->setAlignment(Qt::AlignCenter);
  root->addWidget(current_caption);
  root->addWidget(current_value_);

  auto * timing_grid = new QGridLayout();
  timing_grid->setSpacing(8);
  auto * last_caption = new QLabel("LAST");
  auto * best_caption = new QLabel("BEST");
  last_caption->setObjectName("caption");
  best_caption->setObjectName("caption");
  last_caption->setAlignment(Qt::AlignCenter);
  best_caption->setAlignment(Qt::AlignCenter);
  last_value_ = new QLabel("--:--.---");
  best_value_ = new QLabel("--:--.---");
  last_value_->setObjectName("timingValue");
  best_value_->setObjectName("bestValue");
  last_value_->setAlignment(Qt::AlignCenter);
  best_value_->setAlignment(Qt::AlignCenter);
  timing_grid->addWidget(last_caption, 0, 0);
  timing_grid->addWidget(best_caption, 0, 1);
  timing_grid->addWidget(last_value_, 1, 0);
  timing_grid->addWidget(best_value_, 1, 1);
  root->addLayout(timing_grid);

  auto * history_caption = new QLabel("LAP HISTORY");
  history_caption->setObjectName("caption");
  history_value_ = new QLabel("NO COMPLETED LAPS");
  history_value_->setObjectName("history");
  history_value_->setAlignment(Qt::AlignTop | Qt::AlignLeft);
  history_value_->setMinimumHeight(125);
  history_value_->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Expanding);
  root->addWidget(history_caption);
  root->addWidget(history_value_, 1);

  setStyleSheet(R"(
    QWidget#raceDashboard {
      background-color: #0a0c10;
      color: #f5f7fa;
      font-family: "DejaVu Sans";
    }
    QLabel#series {
      color: #ff1e2d;
      font-size: 11px;
      font-weight: 800;
      letter-spacing: 2px;
    }
    QLabel#title {
      color: #ffffff;
      font-size: 22px;
      font-weight: 900;
    }
    QFrame#redLine { background-color: #e10600; border: none; }
    QLabel#caption {
      color: #8b919d;
      font-size: 10px;
      font-weight: 700;
      letter-spacing: 1px;
    }
    QLabel#statusWaiting, QLabel#statusOutLap, QLabel#statusRacing {
      border-radius: 4px;
      padding: 6px;
      font-size: 12px;
      font-weight: 900;
    }
    QLabel#statusWaiting { background-color: #343944; color: #d4d7dd; }
    QLabel#statusOutLap { background-color: #5a4210; color: #ffc83d; }
    QLabel#statusRacing { background-color: #123f2c; color: #42f59e; }
    QFrame#lapFrame {
      background-color: #12151c;
      border: 1px solid #252a35;
      border-radius: 6px;
    }
    QLabel#lapValue {
      color: #ffffff;
      font-family: "DejaVu Sans Mono";
      font-size: 48px;
      font-weight: 900;
    }
    QLabel#lapSubtitle { color: #7e8592; font-size: 10px; font-weight: 700; }
    QLabel#currentTime {
      color: #ffffff;
      background-color: #151820;
      border-left: 5px solid #e10600;
      padding: 12px 5px;
      font-family: "DejaVu Sans Mono";
      font-size: 25px;
      font-weight: 900;
    }
    QLabel#timingValue, QLabel#bestValue {
      background-color: #151820;
      padding: 9px 4px;
      font-family: "DejaVu Sans Mono";
      font-size: 14px;
      font-weight: 700;
    }
    QLabel#bestValue { color: #d978ff; }
    QLabel#history {
      color: #d7dae0;
      background-color: #101218;
      border-top: 1px solid #2a2f39;
      padding: 10px;
      font-family: "DejaVu Sans Mono";
      font-size: 12px;
    }
  )");
}

RaceDashboardPanel::~RaceDashboardPanel() = default;

void RaceDashboardPanel::onInitialize()
{
  node_ptr_ = getDisplayContext()->getRosNodeAbstraction().lock();
  auto node = node_ptr_->get_raw_node();

  status_sub_ = node->create_subscription<std_msgs::msg::String>(
    "/competition/race_status", 10,
    [this](const std_msgs::msg::String & msg) {
      const auto value = msg.data;
      QMetaObject::invokeMethod(
        this, [this, value]() {updateStatus(value);}, Qt::QueuedConnection);
    });
  current_sub_ = node->create_subscription<std_msgs::msg::Float32>(
    "/competition/current_lap_time", 10,
    [this](const std_msgs::msg::Float32 & msg) {
      const auto value = msg.data;
      QMetaObject::invokeMethod(
        this, [this, value]() {updateCurrent(value);}, Qt::QueuedConnection);
    });
  last_sub_ = node->create_subscription<std_msgs::msg::Float32>(
    "/competition/last_lap_time", 10,
    [this](const std_msgs::msg::Float32 & msg) {
      const auto value = msg.data;
      QMetaObject::invokeMethod(
        this, [this, value]() {updateLast(value);}, Qt::QueuedConnection);
    });
  best_sub_ = node->create_subscription<std_msgs::msg::Float32>(
    "/competition/best_lap_time", 10,
    [this](const std_msgs::msg::Float32 & msg) {
      const auto value = msg.data;
      QMetaObject::invokeMethod(
        this, [this, value]() {updateBest(value);}, Qt::QueuedConnection);
    });
  count_sub_ = node->create_subscription<std_msgs::msg::Int32>(
    "/competition/lap_count", 10,
    [this](const std_msgs::msg::Int32 & msg) {
      const auto value = msg.data;
      QMetaObject::invokeMethod(
        this, [this, value]() {updateLapCount(value);}, Qt::QueuedConnection);
    });
  history_sub_ = node->create_subscription<std_msgs::msg::Float32MultiArray>(
    "/competition/lap_history", 10,
    [this](const std_msgs::msg::Float32MultiArray & msg) {
      const auto value = msg.data;
      QMetaObject::invokeMethod(
        this, [this, value]() {updateHistory(value);}, Qt::QueuedConnection);
    });
}

QString RaceDashboardPanel::formatTime(float seconds)
{
  if (seconds <= 0.0F) {
    return "--:--.---";
  }
  const int minutes = static_cast<int>(seconds) / 60;
  const double remainder = static_cast<double>(seconds) - (minutes * 60.0);
  return QString("%1:%2")
    .arg(minutes, 2, 10, QChar('0'))
    .arg(remainder, 6, 'f', 3, QChar('0'));
}

void RaceDashboardPanel::refreshLapDisplay()
{
  if (status_ == "RACING") {
    lap_value_->setText(
      QString::number(completed_laps_ + 1).rightJustified(2, '0'));
    lap_subtitle_->setText(
      QString("%1 COMPLETED").arg(completed_laps_));
  } else if (status_ == "OUT_LAP") {
    lap_value_->setText("--");
    lap_subtitle_->setText("OUT LAP");
  } else {
    lap_value_->setText("--");
    lap_subtitle_->setText("WAITING FOR DATA");
  }
}

void RaceDashboardPanel::updateStatus(const std::string & status)
{
  status_ = status;
  if (status == "RACING") {
    status_value_->setObjectName("statusRacing");
    status_value_->setText("●  RACING");
  } else if (status == "OUT_LAP") {
    status_value_->setObjectName("statusOutLap");
    status_value_->setText("●  OUT LAP");
  } else {
    status_value_->setObjectName("statusWaiting");
    status_value_->setText("●  WAITING");
  }
  status_value_->style()->unpolish(status_value_);
  status_value_->style()->polish(status_value_);
  refreshLapDisplay();
}

void RaceDashboardPanel::updateCurrent(float seconds)
{
  current_value_->setText(formatTime(seconds));
}

void RaceDashboardPanel::updateLast(float seconds)
{
  last_value_->setText(formatTime(seconds));
}

void RaceDashboardPanel::updateBest(float seconds)
{
  best_value_->setText(formatTime(seconds));
}

void RaceDashboardPanel::updateLapCount(int count)
{
  completed_laps_ = std::max(0, count);
  refreshLapDisplay();
}

void RaceDashboardPanel::updateHistory(const std::vector<float> & history)
{
  if (history.empty()) {
    history_value_->setText("NO COMPLETED LAPS");
    return;
  }

  QString text;
  const auto first = history.size() > 6 ? history.size() - 6 : 0;
  for (std::size_t index = first; index < history.size(); ++index) {
    text += QString("LAP %1     %2")
      .arg(static_cast<int>(index + 1), 2, 10, QChar('0'))
      .arg(formatTime(history[index]));
    if (index + 1 < history.size()) {
      text += "\n";
    }
  }
  history_value_->setText(text);
}

}  // namespace competition_ui

PLUGINLIB_EXPORT_CLASS(competition_ui::RaceDashboardPanel, rviz_common::Panel)
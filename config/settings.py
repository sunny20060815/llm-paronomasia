# API配置
API_KEY = "sk-"  # DeepSeek API密钥
API_BASE_URL = "https://api.deepseek.com/v1"

# 全局参数设置
DEFAULT_TEMPERATURE = 0.8  # 提高创造性
MAX_TOKENS = 4096  # 增加输出长度
TOP_P = 0.95  # 提高多样性

# 房间参数
MAX_CHARACTERS = 8  # 增加房间最大角色数以适应更多互动
MEMORY_WINDOW = 200  # 增加记忆窗口以存储更多历史
INTERACTION_COOLDOWN = 1  # 减少互动冷却时间以增加互动频率

# 日志设置
LOG_LEVEL = "INFO"
LOG_FILE = "virtual_room.log"

# 渲染设置
COLOR_ENABLED = True  # 启用彩色输出
DISPLAY_TIMESTAMP = True  # 显示时间戳

# 角色行为设置
EMOTION_UPDATE_INTERVAL = 5  # 情绪更新间隔（秒）
ACTION_UPDATE_INTERVAL = 10  # 行为更新间隔（秒）
MEMORY_RETENTION_DAYS = 7  # 记忆保留天数

# 符号显示设置
CHARACTER_SYMBOL = "@"  # 角色显示符号
EMOTION_SEPARATOR = ":"  # 情绪分隔符
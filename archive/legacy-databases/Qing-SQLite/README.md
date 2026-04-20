# Qing-SQLite

🌿 轻量级 SQLite 3.52.0 镜像仓库

## 📦 内容

本仓库包含 SQLite 核心源码（Amalgamation 版本），共 4 个文件：

| 文件 | 大小 | 说明 |
|------|------|------|
| `sqlite3.c` | ~9.4MB | 完整引擎实现（单文件） |
| `sqlite3.h` | ~680KB | 公共 API 头文件 |
| `sqlite3ext.h` | ~39KB | 扩展 API 头文件 |
| `shell.c` | ~1.2MB | 命令行 Shell 源码 |

## 🚀 快速开始

### 编译 SQLite

#### Windows (MSVC)

```cmd
:: 使用 Visual Studio Developer Command Prompt
cl sqlite3.c shell.c /Fe:sqlite3.exe /O2
```

#### Windows (MinGW)

```cmd
gcc sqlite3.c shell.c -o sqlite3.exe -O2
```

#### Linux / macOS

```bash
gcc sqlite3.c shell.c -o sqlite3 -O2 -lpthread -ldl
```

### 使用预编译版本

**Windows**: 下载官方预编译工具
```
https://sqlite.org/2026/sqlite-tools-win-x64-3520000.zip
```

## 📖 基本信息

- **版本**: 3.52.0 (2026)
- **来源**: https://sqlite.org/download.html
- **版权**: Public Domain (公共领域)
- **官方文档**: https://sqlite.org/docs.html

## 🔧 编译选项

常用编译宏：

```c
#define SQLITE_ENABLE_JSON1      // 启用 JSON 支持
#define SQLITE_ENABLE_FTS5       // 启用全文搜索
#define SQLITE_ENABLE_RTREE      // 启用 R-Tree 索引
#define SQLITE_THREADSAFE 1      // 线程安全
```

编译示例：
```bash
gcc sqlite3.c shell.c -o sqlite3 -O2 \
  -DSQLITE_ENABLE_JSON1 \
  -DSQLITE_ENABLE_FTS5 \
  -lpthread -ldl
```

## 📊 代码统计

```
sqlite3.c      ~250,000 行 C 代码
sqlite3.h      ~10,000 行 API 声明
shell.c        ~25,000 行 Shell 实现
总计           ~285,000 行
```

## ✅ 编译测试

**测试时间**: 2026-03-09  
**测试平台**: WSL2 (Ubuntu 24.04)  
**编译器**: GCC 13.3.0

### 编译命令

```bash
gcc sqlite3.c shell.c -o sqlite3 -O2 \
  -DSQLITE_ENABLE_JSON1 \
  -DSQLITE_ENABLE_FTS5 \
  -lpthread -ldl -lm \
  -march=native
```

### 测试结果

| 项目 | 结果 |
|------|------|
| **编译** | ✅ 成功 |
| **二进制大小** | 1.7 MB |
| **版本输出** | ✅ 3.52.0 |
| **基础 SQL** | ✅ 正常 |
| **JSON1 扩展** | ✅ 正常 |
| **FTS5 全文搜索** | ✅ 正常 |

### 测试截图

```
$ ./sqlite3 --version
3.52.0 2026-03-06 16:01:44

$ ./sqlite3 < test.sql
3.52.0
1|Qing|qing@example.com
2|Test User|test@example.com

$ ./sqlite3 < test-extensions.sql
JSON Test:
{"name":"Qing","version":"3.52.0"}
FTS5 Test:
SQLite 教程
```

## 🛠️ 定制修改

由于 SQLite 是公共领域软件，你可以：

1. ✅ 自由修改源码
2. ✅ 编译定制版本
3. ✅ 移除不需要的功能（减小体积）
4. ✅ 添加自定义扩展
5. ✅ 用于商业用途（无需授权）

### 精简示例

移除不需要的功能以减小体积：

```c
// 在 sqlite3.c 或编译时定义
#define SQLITE_OMIT_COMPLETE       // 移除 COMPLETE 命令
#define SQLITE_OMIT_EXPLAIN        // 移除 EXPLAIN
#define SQLITE_OMIT_TRIGGER        // 移除触发器（如不需要）
```

## 📚 使用示例

### C 语言

```c
#include "sqlite3.h"
#include <stdio.h>

int main() {
    sqlite3 *db;
    char *err_msg = 0;
    
    int rc = sqlite3_open("test.db", &db);
    
    if (rc != SQLITE_OK) {
        fprintf(stderr, "Cannot open database: %s\n", sqlite3_errmsg(db));
        sqlite3_close(db);
        return 1;
    }
    
    const char *sql = "CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, name TEXT);";
    
    rc = sqlite3_exec(db, sql, 0, 0, &err_msg);
    
    if (rc != SQLITE_OK) {
        fprintf(stderr, "SQL error: %s\n", err_msg);
        sqlite3_free(err_msg);
        sqlite3_close(db);
        return 1;
    }
    
    printf("Database created successfully!\n");
    sqlite3_close(db);
    return 0;
}
```

编译运行：
```bash
gcc main.c sqlite3.c -o app -O2
./app
```

## 🔗 相关链接

- **官方网站**: https://sqlite.org
- **官方下载**: https://sqlite.org/download.html
- **文档**: https://sqlite.org/docs.html
- **C API**: https://sqlite.org/c3ref/intro.html
- **语法**: https://sqlite.org/lang.html

## 📝 更新日志

### v3.52.0 (2026-03-09)
- 初始镜像
- SQLite 3.52.0 Amalgamation
- 包含完整核心功能

---

**许可证**: Public Domain (公共领域)

**维护**: Qing Personal

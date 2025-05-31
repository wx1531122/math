# 小学生数学题目辅助系统 (Elementary Math Problem Assistant)

## 1. 项目简介 (Overview)

本项目旨在开发一个帮助用户管理和生成小学生数学题目的辅助系统。初期版本 (MVP) 将专注于从现有纸质材料中录入题目和答案，并利用 Google Gemini API 为题目生成详细的解题步骤。系统最终能将题目和答案导出为适合 A4 纸打印的格式。

## 2. 项目需求 (Program Requirements)

* **用户群体：** 主要面向需要为小学生准备数学练习的教育者或家长。
* **题目来源：** 初期支持从纸质书籍或其他材料中手动录入题目。
* **题目类型：** 覆盖小学数学的主要题型，包括：
    * 算术运算 (加、减、乘、除)
    * 简单代数概念 (如带未知数 x 的简单等式)
    * 基础几何图形认知 (如周长、面积的简单计算)
    * 应用题 (结合实际生活场景的数学问题)
* **核心功能：**
    1.  **题目手动录入：** 用户能够输入题目的文本内容。
    2.  **答案手动录入：** 用户能够为每个题目输入对应的正确答案。
    3.  **解题步骤生成 (集成 Gemini API)：**
        * 系统应能调用 Google Gemini API。
        * 根据题目文本 (以及可选的答案)，请求 API 生成详细的、适合小学生理解的解题步骤。
        * 存储 API 返回的解题步骤。
    4.  **数据导出：**
        * 用户能够将存储的题目导出。
        * 用户能够将题目连同其对应的答案和解题步骤一起导出。
        * 导出格式应方便在 A4 纸上打印。
* **非功能性需求 (MVP 阶段)：**
    * 系统以命令行界面 (CLI) 运行。
    * 不包含用户账户管理、在线答题、自动批改等复杂交互功能。

## 3. 最终目标 (Final Goals)

* **高效的题目管理：** 建立一个方便用户积累、分类和检索小学数学题目的电子题库。
* **辅助教学与学习：** 通过 Gemini API 生成的详细解题步骤，帮助学生理解解题过程，或为教师/家长提供教学参考。
* **便捷的练习生成：** 能够轻松组合和打印定制化的练习卷。
* **(远期)** 可能扩展支持更丰富的题目格式、更智能的题目推荐、用户交互等。

## 4. 当前实现的技术方案 (MVP Technical Design)

### 4.1. 技术栈

* **编程语言：** Python 3.x
* **数据存储：** CSV 文件 (初期 MVP)
* **核心外部库：**
    * `google-generativeai`: 用于与 Google Gemini API 交互。
* **Python 标准库：** `csv`, `json` (可能用于配置或辅助), `os` 等。

### 4.2. 系统模块划分

* **`main_cli.py` (主命令行界面)：**
    * 作为用户与系统交互的入口。
    * 提供菜单选项，引导用户执行不同操作（如录入题目、生成步骤、导出题目等）。
* **`problem_manager.py` (题目管理器)：**
    * 负责题目的增、删、改、查操作。
    * 具体功能：
        * 从 CSV 文件加载题目数据到内存。
        * 将新题目或更新后的题目数据保存回 CSV 文件。
        * 提供接口供其他模块查询题目信息。
* **`gemini_integration.py` (Gemini API 集成器)：**
    * 封装与 Google Gemini API 通信的逻辑。
    * 构建合适的提示 (Prompt) 发送给 API，以获取针对小学生、详细清晰的解题步骤。
    * 处理 API 的响应，提取所需信息。
    * 包含必要的错误处理机制 (如 API 调用失败、网络问题等)。
* **`exporter.py` (导出器)：**
    * 负责将题目数据格式化并导出到文件。
    * MVP 阶段目标是导出为 **HTML 格式**，以便通过浏览器进行预览和 A4 打印。HTML 将包含基础的样式，确保打印效果清晰。
    * 支持导出仅题目列表，或题目、答案、解题步骤的完整列表。

### 4.3. 数据结构 (CSV 文件格式)

CSV 文件的每一行代表一个题目，包含以下列：

1.  `problem_id`: 题目的唯一标识符 (例如，自动生成的 P001, P002, ...)。
2.  `problem_text`: 题目的完整文本内容。对于特殊数学符号，初期尽量使用通用键盘字符和文字描述 (例如 `*` 或 `x` 代表乘法, `/` 代表除法, `1/2` 代表分数，图形用文字描述其关键特征)。
3.  `problem_type`: 题目的分类 (例如："算术", "应用题", "几何", "代数初步")。
4.  `answer`: 题目的正确答案。
5.  `solution_steps_gemini`: (可选) 由 Gemini API 生成的解题步骤文本。
6.  `source`: (可选) 题目的来源信息 (例如："某某教材 P25 T3")。

### 4.4. 核心工作流程

1.  **题目输入：** 用户通过 `main_cli.py` 选择录入功能，输入题目文本、类型、答案和可选的来源。`problem_manager.py` 将新题目存入 CSV。
2.  **解题步骤生成：** 用户选择某题目，通过 `main_cli.py` 请求生成步骤。`gemini_integration.py` 调用 API，获取步骤后，`problem_manager.py` 将其更新到对应题目的 CSV 记录中。
3.  **题目导出：** 用户选择导出功能。`exporter.py` 从 `problem_manager.py` 获取所需题目数据，生成 HTML 文件。用户可打开 HTML 文件进行打印。MVP 阶段支持导出全部题目或按类型筛选后导出。

### 4.5. 错误处理

* 对文件操作 (读写 CSV) 进行 `try-except` 块处理，捕获 `FileNotFoundError`, `IOError` 等，并向用户提示。
* 对 Gemini API 调用进行 `try-except` 块处理，捕获网络连接、API 认证或限流等可能发生的错误，并向用户提示。

## 5. 未来可能的扩展 (Future Considerations)

* **图形用户界面 (GUI)：** 使用如 Tkinter, PyQt, 或者简单的 Web 界面 (Flask/Django) 替代命令行。
* **更灵活的题目选择导出：** 支持用户勾选或输入多个不连续的题目 ID 进行导出。
* **更丰富的导出格式：** 直接生成 PDF 或 Word (.docx) 文件。
* **LaTeX 支持：** 更好地支持复杂数学公式的录入和显示。
* **本地数据库：** 从 CSV 迁移到 SQLite 或更大型的数据库，以支持更高效的数据管理和查询。
* **题目难度分级与智能推荐。**
* **OCR 辅助录入：** 从图片中识别题目文本（较复杂）。

## 6. 如何开始 (Getting Started)

This section provides instructions on how to set up and run the Elementary Math Problem Assistant.

### 6.1. 先决条件 (Prerequisites)

*   **Python 3.x:** Ensure you have Python 3 (version 3.7 or newer recommended) installed on your system. You can download it from [python.org](https://www.python.org/).

### 6.2. 依赖安装 (Dependencies)

The primary external dependency is the `google-generativeai` library for interacting with the Google Gemini API.

1.  **Install the library using pip:**
    Open your terminal or command prompt and run:
    ```bash
    pip install google-generativeai
    ```
    This command will also install any necessary sub-dependencies.

### 6.3. 配置 (Configuration)

#### Google Gemini API Key

The system requires a Google Gemini API Key to generate detailed solution steps for the math problems.

1.  **Obtain an API Key:**
    *   Visit the [Google AI Studio](https://aistudio.google.com/) (formerly Google Makersuite).
    *   Create a new API key if you don't have one already.

2.  **Set the API Key as an Environment Variable:**
    The application expects the API key to be available as an environment variable named `GEMINI_API_KEY`.

    *   **For Linux/macOS (bash/zsh):**
        Open your terminal and run:
        ```bash
        export GEMINI_API_KEY="YOUR_API_KEY_HERE"
        ```
        Replace `"YOUR_API_KEY_HERE"` with your actual API key. To make this permanent, add this line to your shell's configuration file (e.g., `~/.bashrc`, `~/.zshrc`) and then source it (e.g., `source ~/.bashrc`) or open a new terminal session.

    *   **For Windows (Command Prompt):**
        ```cmd
        set GEMINI_API_KEY=YOUR_API_KEY_HERE
        ```
        Replace `YOUR_API_KEY_HERE` with your actual API key. This command sets the variable for the current session only. For a more permanent solution, you can set it via "Environment Variables" in System Properties.

    *   **For Windows (PowerShell):**
        ```powershell
        $env:GEMINI_API_KEY="YOUR_API_KEY_HERE"
        ```
        Replace `"YOUR_API_KEY_HERE"` with your actual API key. This sets the variable for the current session. To make it permanent, you can add this to your PowerShell profile script.

    **Important:** If the `GEMINI_API_KEY` environment variable is not set or is invalid, the solution generation feature will still run but will provide mock/placeholder responses instead of actual AI-generated steps. Other functionalities of the application (adding problems, viewing, exporting without solutions) will work normally.

### 6.4. 运行程序 (Running the Program)

Once dependencies are installed and the API key is configured (optional for basic use, required for solution generation):

1.  **Navigate to the project directory:**
    Open your terminal or command prompt and change to the directory where you have saved the project files (e.g., `main_cli.py`, `problem_manager.py`, etc.).
    ```bash
    cd path/to/your/project_directory
    ```

2.  **Run the main command-line interface:**
    ```bash
    python main_cli.py
    ```

3.  **Using the Application:**
    Upon running the command, a menu will appear with the following options:
    *   **Add New Problem:** Allows you to input the problem text, type, answer, and an optional source.
    *   **Generate Solution Steps:** Prompts for a Problem ID and uses the Gemini API (if configured) to generate solution steps.
    *   **View All Problems:** Displays all problems currently stored in the `data/problems.csv` file.
    *   **Export Problems to HTML:** Allows you to export problems (all or filtered by type, with or without solutions) to an HTML file suitable for viewing and printing.
    *   **Exit:** Closes the application.

    Follow the on-screen prompts to interact with the system. The problem data will be stored in a `data` subdirectory (created automatically if it doesn't exist) in a file named `problems.csv`.

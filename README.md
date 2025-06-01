# 小学生数学题目辅助 Web 系统 (Elementary Math Problem Assistant - Web App)

## 1. 项目简介 (Overview)

本项目旨在开发一个基于 Web 的辅助系统，帮助用户管理和生成小学生数学题目。用户可以通过 Web 界面录入题目和答案，系统将利用 Google Gemini API 为题目生成详细的解题步骤。最终，用户能够方便地将题目和答案导出为适合打印的格式。

## 2. 项目需求 (Program Requirements)

* **用户群体：** 主要面向需要为小学生准备数学练习的教育者或家长。
* **题目来源：** 初期支持用户通过 Web 界面手动录入题目。
* **题目类型：** 覆盖小学数学的主要题型，包括：
    * 算术运算 (加、减、乘、除)
    * 简单代数概念 (如带未知数 x 的简单等式)
    * 基础几何图形认知 (如周长、面积的简单计算)
    * 应用题 (结合实际生活场景的数学问题)
* **核心功能：**
    1.  **题目 Web 录入：** 用户能够通过 Web 表单输入题目的文本内容、类型、答案和来源。
    2.  **解题步骤生成 (集成 Gemini API)：**
        * 后端系统应能调用 Google Gemini API。
        * 根据题目文本，请求 API 生成详细的、适合小学生理解的解题步骤。
        * 在 Web 界面上展示题目、答案和解题步骤。
    3.  **数据存储与管理：** 题目、答案及解题步骤等信息将存储在后端。
    4.  **数据导出：**
        * 用户能够通过 Web 界面将选定或全部题目导出。
        * 导出格式应方便在 A4 纸上打印 (例如，生成 HTML 或 PDF)。
* **非功能性需求：**
    * 用户友好的 Web 界面。
    * 前后端分离架构。

## 3. 最终目标 (Final Goals)

* **高效的题目管理：** 建立一个方便用户通过 Web 界面积累、分类和检索小学数学题目的电子题库。
* **辅助教学与学习：** 通过 Gemini API 生成的详细解题步骤，帮助学生理解解题过程，或为教师/家长提供教学参考。
* **便捷的练习生成：** 能够通过 Web 界面轻松组合和打印定制化的练习卷。
* **(远期)** 可能扩展支持更丰富的题目格式、用户账户管理、在线互动练习、更智能的题目推荐等。

## 4. 当前实现的技术方案 (MVP - Web Application)

### 4.1. 技术栈

* **前端 (Frontend)：**
    * **语言：** TypeScript
    * **框架：** Next.js
    * **样式：** Tailwind CSS
    * **状态管理：** (根据 Next.js 版本和需求，可选用 React Context, Zustand, Redux Toolkit 等)
    * **数据请求：** Fetch API, SWR, or React Query
* **后端 (Backend)：**
    * **语言：** Python
    * **框架：** Flask
    * **API 设计：** RESTful API
* **数据存储：**
    * 初期 MVP：CSV 文件（由 Python 后端管理）
    * 后续迭代：SQLite 或其他数据库 (如 PostgreSQL, MySQL)
* **核心外部库 (Python)：**
    * `google-generativeai`: 用于与 Google Gemini API 交互
    * Python Web 框架对应的库
* **Python 标准库：** `csv`, `os`, `html` (用于导出)

### 4.2. 系统架构

* **前后端分离：**
    * **前端 (Next.js)：** 负责用户界面的展示、用户输入处理、向后端发送 API 请求以及展示从后端获取的数据。
    * **后端 (Python Web 框架)：** 负责处理业务逻辑、与 Gemini API 交互、管理数据存储 (CSV 文件或数据库)，并向前端提供 API 接口。

### 4.3. 模块划分 (概念性)

* **前端模块 (Next.js Components/Pages):**
    * `ProblemInputForm`: 用于录入新题目的表单组件。
    * `ProblemListView`: 展示题目列表的页面/组件。
    * `ProblemDetailView`: 展示单个题目详情（包括答案和解题步骤）的页面/组件。
    * `ExportControls`: 用于触发导出功能的组件。
* **后端模块 (Python - 依赖所选框架的组织方式):**
    * **API Endpoints/Routes:**
        * `POST /api/problems`: 添加新题目。
        * `GET /api/problems`: 获取题目列表。
        * `GET /api/problems/<problem_id>`: 获取特定题目详情。
        * `POST /api/problems/<problem_id>/generate_solution`: 为特定题目请求生成解题步骤。
        * `PUT /api/problems/<problem_id>`: 更新题目信息 (例如添加解题步骤)。
        * `GET /api/export/problems`: 导出题目 (可带参数控制导出内容和格式)。
    * **Service Layer/Business Logic:**
        * `ProblemService`: 封装题目管理的业务逻辑，如与 `problem_manager.py` (或其等效数据库操作模块) 交互。
        * `GeminiService`: 封装与 `gemini_integration.py` (或其等效功能) 交互的逻辑。
    * **Data Access Layer:**
        * `problem_manager.py` (初期): 继续使用或改造，使其适应 Web 后端的需求，负责 CSV 文件的读写。
        * (未来) 数据库 ORM 或查询模块。
    * `exporter.py` (改造): 可能需要调整以适应从 Web 请求触发导出，并可能直接返回文件流或生成文件供下载。

### 4.4. 数据结构 (CSV 文件格式 - 初期保持不变)

CSV 文件的每一行代表一个题目，包含以下列：

1.  `problem_id`: 题目的唯一标识符 (例如，自动生成的 P001, P002, ...)。
2.  `problem_text`: 题目的完整文本内容。
3.  `problem_type`: 题目的分类。
4.  `answer`: 题目的正确答案。
5.  `solution_steps_gemini`: (可选) 由 Gemini API 生成的解题步骤文本。
6.  `source`: (可选) 题目的来源信息。

### 4.5. 核心工作流程 (Web App)

1.  **题目输入 (Web)：** 用户在前端 Next.js 应用的表单中输入题目信息。前端将数据发送到 Python 后端的 `/api/problems` POST 端点。后端 `ProblemService` 调用 `problem_manager.py` 将新题目存入 CSV。
2.  **解题步骤生成 (Web)：** 用户在前端查看某个题目时，点击“生成解题步骤”按钮。前端向后端 `/api/problems/<problem_id>/generate_solution` POST 端点发送请求。后端 `GeminiService` 调用 Gemini API，获取步骤后，通过 `ProblemService` 和 `problem_manager.py` 更新 CSV 中对应题目的记录。前端随后刷新题目详情以展示新步骤。
3.  **题目导出 (Web)：** 用户在前端选择导出选项。前端向后端 `/api/export/problems` GET 端点发送请求。后端 `exporter.py` (或其改造版本) 获取数据，生成 HTML (或未来 PDF)，并将其作为文件下载响应返回给用户浏览器。

### 4.6. 错误处理

* **前端：** 在用户界面上显示清晰的错误提示（例如，表单验证错误、API 请求失败）。
* **后端：** 返回合适的 HTTP 状态码和错误信息给前端。对文件操作和 API 调用进行详细的日志记录和异常捕获。

## 5. 未来可能的扩展 (Future Considerations)

* **用户认证与授权：** 允许多用户使用并管理各自的题库。
* **富文本编辑器：** 用于题目输入，更好地支持数学符号和格式。
* **数据库迁移：** 从 CSV 迁移到 SQLite 或更强大的数据库。
* **更高级的导出选项：** PDF 导出，Word 文档导出。
* **实时协作或分享功能。**
* **题目难度自动评估与智能推荐。**

## 6. 如何开始 (Getting Started - Updated for Web App)

*(这部分将更加详细，并分为前端和后端)*

### 6.1. 先决条件 (Prerequisites)

* **Node.js 和 npm/yarn:** 用于前端 Next.js 开发。
* **Python 3.x:** 用于后端 Python 开发。
* **(可选) Git:** 用于版本控制。

### 6.2. 依赖安装 (Dependencies)

* **前端 (在前端项目目录下运行):**
    ```bash
    # 使用 npm
    npm install typescript next react react-dom tailwindcss postcss autoprefixer # ...以及其他前端库
    npm install -D @types/react @types/node
    # 或使用 yarn
    yarn add typescript next react react-dom tailwindcss postcss autoprefixer # ...以及其他前端库
    yarn add -D @types/react @types/node
    ```
* **后端 (在后端项目目录下，建议使用虚拟环境):**
    ```bash
    # 创建并激活虚拟环境 (示例)
    python -m venv venv
    # Windows: venv\Scripts\activate
    # macOS/Linux: source venv/bin/activate

    pip install google-generativeai #
    pip install <选定的 Python Web 框架，例如 flask, fastapi, uvicorn>
    # 其他可能需要的库
    ```

### 6.3. 配置 (Configuration)

#### Google Gemini API Key

后端 Python 应用需要 Google Gemini API Key。设置方式与之前 CLI 版本类似，通过环境变量 `GEMINI_API_KEY`。

#### 前后端连接

* 前端应用需要知道后端 API 的地址 (例如 `http://localhost:8000/api`，如果后端运行在 8000 端口)。这通常通过前端的环境变量配置 (例如 Next.js 中的 `.env.local` 文件)。

### 6.4. 运行程序 (Running the Program)

1.  **启动后端服务：**
    * 导航到后端项目目录。
    * 激活虚拟环境。
    * 根据所选的 Python Web 框架启动开发服务器 (例如，使用 `uvicorn main:app --reload` 启动 FastAPI 应用，或 `flask run` 启动 Flask 应用)。
2.  **启动前端开发服务器：**
    * 导航到前端项目目录。
    * 运行 (例如，使用 npm):
        ```bash
        npm run dev
        # 或使用 yarn
        yarn dev
        ```
3.  **访问 Web 应用：**
    在浏览器中打开前端应用的地址 (通常是 `http://localhost:3000`)。

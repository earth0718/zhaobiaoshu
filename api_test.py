import requests
import json
import time
import os

BASE_URL = "http://localhost:8000"

# 用于测试的文件，请确保这些文件存在
TEST_TXT_FILE = "test.txt"
TEST_PDF_FILE = "test (2).pdf"
TEST_DOCX_FILE = "test (2).docx"

# 全局变量，用于存储测试过程中产生的ID
last_task_id = None
last_record_id = None
last_gender_book_task_id = None

def print_response(response):
    """格式化打印响应信息"""
    print(f">>> URL: {response.url}")
    print(f">>> Status Code: {response.status_code}")
    try:
        print(f">>> Response JSON: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except (json.JSONDecodeError, AttributeError):
        # Handle cases where response is not JSON or doesn't have .json() method (like file downloads)
        content_type = response.headers.get('content-type', '')
        if 'text' in content_type or 'html' in content_type:
            print(f">>> Response Text: {response.text[:500]}...") # Truncate long responses
        else:
            print(f">>> Response Content-Type: {content_type}")
            print(f">>> Response Content Length: {len(response.content)}")
    print("-" * 80)

# --- 1. 系统信息接口 --- #
def test_system_info_endpoints():
    print("\n===== 1. Testing System Information Endpoints =====")
    
    print("--- 1.2. GET /api/info ---")
    try:
        response = requests.get(f"{BASE_URL}/api/info")
        print_response(response)
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")

    print("--- 1.3. GET /health ---")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print_response(response)
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")

    print("--- 1.4. GET /info ---")
    try:
        response = requests.get(f"{BASE_URL}/info")
        print_response(response)
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")

# --- 2. 文档解析模块 --- #
def test_parser_endpoints():
    print("\n===== 2. Testing Document Parser Endpoints =====")

    # Test with TXT file
    if os.path.exists(TEST_TXT_FILE):
        print("--- 2.1.1. POST /api/parser/parse (TXT) ---")
        try:
            with open(TEST_TXT_FILE, "rb") as f:
                files = {"file": (os.path.basename(TEST_TXT_FILE), f, "text/plain")}
                response = requests.post(f"{BASE_URL}/api/parser/parse", files=files)
                print_response(response)
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
    else:
        print(f"警告: {TEST_TXT_FILE} 不存在，跳过 TXT 解析测试。")

    # Test with PDF file
    if os.path.exists(TEST_PDF_FILE):
        print("--- 2.1.2. POST /api/parser/parse (PDF) ---")
        try:
            with open(TEST_PDF_FILE, "rb") as f:
                files = {"file": (os.path.basename(TEST_PDF_FILE), f, "application/pdf")}
                response = requests.post(f"{BASE_URL}/api/parser/parse", files=files)
                print_response(response)
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
    else:
        print(f"警告: {TEST_PDF_FILE} 不存在，跳过 PDF 解析测试。")

    # Test with DOCX file
    if os.path.exists(TEST_DOCX_FILE):
        print("--- 2.1.3. POST /api/parser/parse (DOCX) ---")
        try:
            with open(TEST_DOCX_FILE, "rb") as f:
                files = {"file": (os.path.basename(TEST_DOCX_FILE), f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
                response = requests.post(f"{BASE_URL}/api/parser/parse", files=files)
                print_response(response)
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
    else:
        print(f"警告: {TEST_DOCX_FILE} 不存在，跳过 DOCX 解析测试。")

    # ... 其他解析器接口 ...
    # 为了简化，我们只测试核心的 `parse` 接口，其他接口结构类似
    print("--- 2.5. GET /api/parser/formats ---")
    try:
        response = requests.get(f"{BASE_URL}/api/parser/formats")
        print_response(response)
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")

    print("--- 2.7. GET /api/parser/health ---")
    try:
        response = requests.get(f"{BASE_URL}/api/parser/health")
        print_response(response)
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")

# --- 3. 配置管理模块 --- #
def test_config_endpoints():
    print("\n===== 3. Testing Configuration Management Endpoints =====")
    print("--- 3.1. GET /api/config/parser ---")
    try:
        response = requests.get(f"{BASE_URL}/api/config/parser")
        print_response(response)
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
    # ... 其他配置接口 ...

# --- 4. 招标文件生成模块 --- #
def test_tender_generation_endpoints():
    global last_task_id
    print("\n===== 4. Testing Tender Generation Endpoints =====")
    if not os.path.exists(TEST_DOCX_FILE):
        print(f"错误: 测试文件 {TEST_DOCX_FILE} 不存在，跳过招标文件生成测试。")
        return

    print("--- 4.1. POST /api/tender/generate ---")
    try:
        with open(TEST_DOCX_FILE, "rb") as f:
            files = {"file": (os.path.basename(TEST_DOCX_FILE), f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            response = requests.post(f"{BASE_URL}/api/tender/generate", files=files)
            print_response(response)
            if response.status_code == 200 and response.json().get("task_id"):
                last_task_id = response.json()["task_id"]
                print(f"成功创建任务，Task ID: {last_task_id}")
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")

    if last_task_id:
        print(f"--- 4.3. GET /api/tender/status/{last_task_id} ---")
        try:
            print("等待5秒让任务开始处理...")
            time.sleep(5)
            response = requests.get(f"{BASE_URL}/api/tender/status/{last_task_id}")
            print_response(response)
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")

    print("--- 4.4. GET /api/tender/models ---")
    try:
        response = requests.get(f"{BASE_URL}/api/tender/models")
        print_response(response)
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")

    print("--- 4.7. GET /api/tender/tasks ---")
    try:
        response = requests.get(f"{BASE_URL}/api/tender/tasks")
        print_response(response)
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")

    # --- 危险操作：默认不执行 ---
    # if last_task_id:
    #     print(f"--- 4.8. DELETE /api/tender/tasks/{last_task_id} (DANGEROUS) ---")
    #     # input("按回车键继续删除任务...") # 取消注释以启用
    #     try:
    #         response = requests.delete(f"{BASE_URL}/api/tender/tasks/{last_task_id}")
    #         print_response(response)
    #     except requests.exceptions.RequestException as e:
    #         print(f"请求失败: {e}")

# --- 5. 历史记录模块 --- #
def test_history_endpoints():
    global last_record_id
    print("\n===== 5. Testing History Endpoints =====")
    
    print("--- 5.1. GET /api/history/records ---")
    try:
        response = requests.get(f"{BASE_URL}/api/history/records?limit=5")
        print_response(response)
        if response.status_code == 200 and response.json().get("records"):
            records = response.json()["records"]
            if records:
                last_record_id = records[0].get("record_id")
                print(f"获取到最新记录ID: {last_record_id}")
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")

    if last_record_id:
        print(f"--- 5.2. GET /api/history/records/{last_record_id} ---")
        try:
            response = requests.get(f"{BASE_URL}/api/history/records/{last_record_id}")
            print_response(response)
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")

    print("--- 5.4. GET /api/history/statistics ---")
    try:
        response = requests.get(f"{BASE_URL}/api/history/statistics")
        print_response(response)
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")

    # --- 危险操作：默认不执行 ---
    # if last_record_id:
    #     print(f"--- 5.3. DELETE /api/history/records/{last_record_id} (DANGEROUS) ---")
    #     # input("按回车键继续删除记录...") # 取消注释以启用
    #     try:
    #         response = requests.delete(f"{BASE_URL}/api/history/records/{last_record_id}")
    #         print_response(response)
    #     except requests.exceptions.RequestException as e:
    #         print(f"请求失败: {e}")

    # print("--- 5.6. DELETE /api/history/records (EXTREMELY DANGEROUS) ---")
    # # input("按回车键继续清空所有历史记录...") # 取消注释以启用
    # try:
    #     response = requests.delete(f"{BASE_URL}/api/history/records")
    #     print_response(response)
    # except requests.exceptions.RequestException as e:
    #     print(f"请求失败: {e}")

# --- 6. 过滤器模块 --- #
def test_filter_endpoints():
    print("\n===== 6. Testing Filter Endpoints =====")
    print("--- 6.1. POST /api/filter/process ---")
    try:
        # 构造一个简单的JSON body
        json_data = {"key": "value", "content": [{"text": "some text"}]}
        response = requests.post(f"{BASE_URL}/api/filter/process", json=json_data)
        print_response(response)
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")

# --- 7. 投标书生成模块 --- #
def test_gender_book_endpoints():
    global last_gender_book_task_id
    print("\n===== 7. Testing Gender Book Endpoints =====")
    print("--- 7.1. POST /api/gender_book/generate_from_json ---")
    try:
        json_data = {
            "tender_document_json": {"content": [{"text": "项目概述", "type": "Title"}]},
            "model_name": "ollama"
        }
        response = requests.post(f"{BASE_URL}/api/gender_book/generate_from_json", json=json_data)
        print_response(response)
        if response.status_code == 200 and response.json().get("task_id"):
            last_gender_book_task_id = response.json()["task_id"]
            print(f"成功创建投标书生成任务，Task ID: {last_gender_book_task_id}")
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")

    if last_gender_book_task_id:
        print(f"--- 7.3. GET /api/gender_book/status/{last_gender_book_task_id} ---")
        try:
            print("等待5秒让任务开始处理...")
            time.sleep(5)
            response = requests.get(f"{BASE_URL}/api/gender_book/status/{last_gender_book_task_id}")
            print_response(response)
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")

    print("--- 7.4. GET /api/gender_book/sections ---")
    try:
        response = requests.get(f"{BASE_URL}/api/gender_book/sections")
        print_response(response)
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")

    print("--- 7.8. GET /api/gender_book/health ---")
    try:
        response = requests.get(f"{BASE_URL}/api/gender_book/health")
        print_response(response)
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")

if __name__ == "__main__":
    print("开始全面测试API接口...")
    print(f"目标服务器: {BASE_URL}")
    print(f"将使用 {TEST_TXT_FILE}、{TEST_PDF_FILE} 和 {TEST_DOCX_FILE} 进行测试。\n")

    # 检查测试文件是否存在
    if not os.path.exists(TEST_TXT_FILE):
        print(f"警告: {TEST_TXT_FILE} 不存在，部分测试将跳过。")
    if not os.path.exists(TEST_PDF_FILE):
        print(f"警告: {TEST_PDF_FILE} 不存在，部分测试将跳过。")
    if not os.path.exists(TEST_DOCX_FILE):
        print(f"警告: {TEST_DOCX_FILE} 不存在，部分测试将跳过。")

    # 按顺序执行所有测试
    test_system_info_endpoints()
    test_parser_endpoints()
    test_config_endpoints()
    test_tender_generation_endpoints()
    test_history_endpoints()
    test_filter_endpoints()
    test_gender_book_endpoints()

    print("\n所有测试已执行完毕。")
    print("请检查上面的输出以确定每个接口的测试结果。")
    print("注意：标记为 (DANGEROUS) 的删除操作默认是注释掉的，不会执行。")
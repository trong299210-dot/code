import random
import io
import sys
import hashlib
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "seen_questions.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS seen_codes (
            code_hash TEXT PRIMARY KEY,
            difficulty TEXT,
            code_content TEXT
        )
    """)
    conn.commit()
    conn.close()

def is_code_seen(code: str) -> bool:
    norm = "".join(code.split())
    code_hash = hashlib.sha256(norm.encode("utf-8")).hexdigest()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM seen_codes WHERE code_hash = ?", (code_hash,))
    row = cursor.fetchone()
    conn.close()
    return row is not None

def mark_code_seen(code: str, difficulty: str):
    norm = "".join(code.split())
    code_hash = hashlib.sha256(norm.encode("utf-8")).hexdigest()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO seen_codes (code_hash, difficulty, code_content) VALUES (?, ?, ?)",
                   (code_hash, difficulty, code))
    conn.commit()
    conn.close()

def get_seen_count():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM seen_codes")
    cnt = cursor.fetchone()[0]
    conn.close()
    return cnt

init_db()

WORDS_POOL = [
    "python", "discord", "algorithm", "variable", "developer", "backend", "machine",
    "learning", "database", "network", "function", "compile", "terminal", "debugger",
    "package", "library", "syntax", "runtime", "virtual", "process", "thread",
    "lambda", "generator", "decorator", "iterator", "bytecode", "asyncio", "coroutine",
    "exception", "pointer", "constant", "pipeline", "cluster", "matrix", "vector"
]
FRUITS = ["apple", "banana", "cherry", "mango", "orange", "grape", "melon", "kiwi", "peach", "berry"]

# ========================================================
# 🟢 1. DỄ (EASY) - GIẢI THÍCH CHI TIẾT TỪNG BƯỚC (STEP-BY-STEP)
# ========================================================
def gen_easy_arithmetic():
    a, b, c = random.randint(3, 80), random.randint(2, 25), random.randint(1, 15)
    t = random.choice([1, 2, 3, 4])
    if t == 1:
        code = f"a = {a}\nb = {b}\nprint(a + b * {c})"
        exp = (
            f"1. Phép toán gồm cộng (+) và nhân (*).\n"
            f"2. Theo thứ tự ưu tiên toán tử trong Python (PEMDAS): phép nhân được tính trước.\n"
            f"3. b * {c} = {b} * {c} = {b * c}.\n"
            f"4. Cuối cùng thực hiện phép cộng: a + {b * c} = {a} + {b * c} = {a + b * c}."
        )
    elif t == 2:
        code = f"x = {a}\ny = {b}\nprint((x + y) // {c})"
        exp = (
            f"1. Biểu thức trong dấu ngoặc đơn `(x + y)` luôn được ưu tiên tính trước.\n"
            f"2. x + y = {a} + {b} = {a + b}.\n"
            f"3. Toán tử `//` là phép chia lấy phần nguyên (Floor Division).\n"
            f"4. {a + b} // {c} = {(a + b) // c} (phần thập phân bị lược bỏ)."
        )
    elif t == 3:
        code = f"x = {a}\ny = {b}\nprint(x % y)"
        exp = (
            f"1. Toán tử `%` (Modulo) dùng để lấy số dư của phép chia.\n"
            f"2. Thực hiện phép chia: {a} / {b} = {a // b} (dư {a % b}).\n"
            f"3. Do đó, kết quả của biểu thức là số dư = {a % b}."
        )
    else:
        code = f"val = {a}\nprint(val // 10 + val % 10)"
        exp = (
            f"1. `val // 10`: Chia lấy phần nguyên cho 10 để tách chữ số hàng chục -> {a} // 10 = {a // 10}.\n"
            f"2. `val % 10`: Chia lấy phần dư cho 10 để tách chữ số hàng đơn vị -> {a} % 10 = {a % 10}.\n"
            f"3. Thực hiện phép cộng: {a // 10} + {a % 10} = {a // 10 + a % 10}."
        )
    return code, exp

def gen_easy_string():
    word = random.choice(WORDS_POOL)
    start = random.randint(0, 2)
    end = random.randint(start + 2, len(word))
    t = random.choice([1, 2, 3])
    if t == 1:
        code = f"s = '{word}'\nprint(len(s))"
        exp = (
            f"1. Hàm tích hợp sẵn `len()` đếm tổng số ký tự có trong chuỗi.\n"
            f"2. Chuỗi '{word}' bao gồm chính xác {len(word)} ký tự.\n"
            f"3. Kết quả in ra màn hình là {len(word)}."
        )
    elif t == 2:
        code = f"s = '{word}'\nprint(s[{start}:{end}])"
        exp = (
            f"1. Cú pháp cắt chuỗi (Slicing) có dạng `s[start:end]`.\n"
            f"2. Python đánh chỉ số index từ 0, lấy từ vị trí start={start} đến end={end} (không bao gồm index {end}).\n"
            f"3. Các ký tự được lấy ra gồm từ index {start} đến {end-1}, tạo thành chuỗi con '{word[start:end]}'."
        )
    else:
        code = f"s = '{word}'\nprint(s[::-1])"
        exp = (
            f"1. Cú pháp slicing đầy đủ: `s[start:stop:step]`.\n"
            f"2. Khi để trống start, stop và đặt `step = -1`, Python sẽ duyệt chuỗi từ ký tự cuối cùng ngược về đầu.\n"
            f"3. Toàn bộ chuỗi '{word}' được đảo ngược thành '{word[::-1]}'."
        )
    return code, exp

def gen_easy_list_ops():
    size = random.randint(3, 6)
    nums = [random.randint(1, 30) for _ in range(size)]
    extra = random.randint(5, 50)
    t = random.choice([1, 2, 3])
    if t == 1:
        code = f"nums = {nums}\nprint(sum(nums))"
        exp = (
            f"1. Hàm `sum()` duyệt qua từng phần tử trong danh sách và tính tổng cộng dồn.\n"
            f"2. Tổng các số: {' + '.join(map(str, nums))} = {sum(nums)}.\n"
            f"3. Kết quả xuất ra màn hình là {sum(nums)}."
        )
    elif t == 2:
        code = f"nums = {nums}\nnums.append({extra})\nprint(nums[-1])"
        exp = (
            f"1. Ban đầu danh sách có {len(nums)} phần tử: {nums}.\n"
            f"2. Phương thức `append({extra})` bổ sung giá trị {extra} vào vị trí cuối cùng của mảng.\n"
            f"3. Chỉ số âm `[-1]` trong Python đại diện cho phần tử ở vị trí cuối cùng, chính là {extra}."
        )
    else:
        code = f"nums = {nums}\nprint(sorted(nums)[1])"
        sorted_nums = sorted(nums)
        exp = (
            f"1. Hàm `sorted(nums)` tạo một danh sách mới được sắp xếp tăng dần: {sorted_nums}.\n"
            f"2. Chỉ số mảng bắt đầu từ 0: index [0] là số nhỏ nhất ({sorted_nums[0]}), index [1] là số nhỏ thứ hai ({sorted_nums[1]}).\n"
            f"3. Do đó `sorted(nums)[1]` in ra giá trị {sorted_nums[1]}."
        )
    return code, exp

def gen_easy_long_score():
    scores = [random.randint(5, 10) for _ in range(4)]
    bonus = random.randint(1, 3)
    calc_total = sum(s + bonus if s >= 8 else s for s in scores)
    avg = calc_total // len(scores)
    code = f"""def calculate_final_grade(scores, bonus):
    total = 0
    for score in scores:
        if score >= 8:
            total += score + bonus
        else:
            total += score
    return total // len(scores)

grades = {scores}
print(calculate_final_grade(grades, {bonus}))"""
    exp = (
        f"1. Khởi tạo `total = 0` và duyệt qua từng điểm số trong {scores}.\n"
        f"2. Kiểm tra điều kiện: Nếu điểm >= 8 thì cộng thêm điểm thưởng ({bonus}), ngược lại giữ nguyên.\n"
        f"3. Tổng điểm tích lũy được sau vòng lặp là total = {calc_total}.\n"
        f"4. Cuối cùng, thực hiện phép chia lấy phần nguyên `total // len(scores)`: {calc_total} // {len(scores)} = {avg}."
    )
    return code, exp

def gen_easy_long_shopping():
    p1, p2, p3 = random.randint(10, 30), random.randint(15, 40), random.randint(5, 20)
    discount = random.randint(5, 10)
    cart = {'book': p1, 'pen': p2, 'ruler': p3}
    tot = sum(p - discount if p > 20 else p for p in cart.values())
    code = f"""cart = {{'book': {p1}, 'pen': {p2}, 'ruler': {p3}}}
total = 0

for item, price in cart.items():
    if price > 20:
        total += price - {discount}
    else:
        total += price

print(total)"""
    exp = (
        f"1. Duyệt qua từng cặp (item, price) trong từ điển giỏ hàng:\n"
        f"   - 'book': giá {p1} -> {p1 - discount if p1 > 20 else p1} (áp dụng giảm giá nếu > 20)\n"
        f"   - 'pen': giá {p2} -> {p2 - discount if p2 > 20 else p2}\n"
        f"   - 'ruler': giá {p3} -> {p3 - discount if p3 > 20 else p3}\n"
        f"2. Cộng dồn tất cả các giá thành sau điều kiện ta được tổng tiền = {tot}."
    )
    return code, exp

EASY_GENS = [gen_easy_arithmetic, gen_easy_string, gen_easy_list_ops, gen_easy_long_score, gen_easy_long_shopping]

# ========================================================
# 🟡 2. TRUNG BÌNH (MEDIUM) - GIẢI THÍCH CHI TIẾT
# ========================================================
def gen_med_comprehension():
    n = random.randint(5, 10)
    m = random.randint(2, 3)
    k = random.randint(2, 4)
    matching = [x for x in range(n) if x % m == 0]
    res = [x * k for x in matching]
    code = f"res = [x * {k} for x in range({n}) if x % {m} == 0]\nprint(res)"
    exp = (
        f"1. `range({n})` sinh dãy số từ 0 đến {n-1}.\n"
        f"2. Mệnh đề điều kiện `if x % {m} == 0` lọc ra các số chia hết cho {m}: {matching}.\n"
        f"3. Biểu thức biến đổi `x * {k}` nhân mỗi phần tử đã lọc với {k}: {res}.\n"
        f"4. Danh sách kết quả cuối cùng in ra là {res}."
    )
    return code, exp

def gen_med_dict_set():
    v1, v2 = random.randint(1, 10), random.randint(1, 10)
    s1 = {v1, v2, v1 + 2}
    s2 = {v2, v1 + 2, v2 + 3}
    inter = sorted(list(s1 & s2))
    code = f"s1 = {{{v1}, {v2}, {v1+2}}}\ns2 = {{{v2}, {v1+2}, {v2+3}}}\nprint(sorted(list(s1 & s2)))"
    exp = (
        f"1. Tập hợp s1 gồm các phần tử duy nhất: {sorted(list(s1))}.\n"
        f"2. Tập hợp s2 gồm các phần tử duy nhất: {sorted(list(s2))}.\n"
        f"3. Toán tử `&` là phép giao (Intersection): tìm các phần tử xuất hiện ở CẢ HAI tập hợp.\n"
        f"4. Các phần tử chung là {inter}. Sau đó `sorted()` sắp xếp tăng dần cho ra {inter}."
    )
    return code, exp

def gen_med_long_class_bank():
    init_bal = random.randint(50, 100)
    dep = random.randint(20, 50)
    wd = random.randint(10, 40)
    fee = random.randint(2, 5)
    bal1 = init_bal + dep
    bal2 = bal1 - (wd + fee)
    code = f"""class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount
        return self.balance

    def withdraw(self, amount, fee=0):
        total = amount + fee
        if self.balance >= total:
            self.balance -= total
        return self.balance

acc = BankAccount('Alice', {init_bal})
acc.deposit({dep})
acc.withdraw({wd}, fee={fee})
print(acc.balance)"""
    exp = (
        f"1. Khởi tạo đối tượng `acc` với số dư ban đầu `balance = {init_bal}`.\n"
        f"2. Gọi `deposit({dep})`: số dư tăng lên {init_bal} + {dep} = {bal1}.\n"
        f"3. Gọi `withdraw({wd}, fee={fee})`: tổng số tiền cần trừ là {wd} + {fee} = {wd + fee}.\n"
        f"4. Vì số dư ({bal1}) >= {wd + fee}, giao dịch thành công: số dư còn {bal1} - {wd + fee} = {bal2}."
    )
    return code, exp

def gen_med_long_inventory():
    p1, p2, p3 = random.randint(2, 5), random.randint(1, 4), random.randint(3, 6)
    inventory = [
        {'name': 'Laptop', 'qty': p1, 'price': 1000},
        {'name': 'Mouse', 'qty': p2, 'price': 50},
        {'name': 'Keyboard', 'qty': p3, 'price': 80}
    ]
    val = sum(item['qty'] * item['price'] for item in inventory if item['qty'] >= 3)
    code = f"""inventory = [
    {{'name': 'Laptop', 'qty': {p1}, 'price': 1000}},
    {{'name': 'Mouse', 'qty': {p2}, 'price': 50}},
    {{'name': 'Keyboard', 'qty': {p3}, 'price': 80}}
]

def total_stock_value(items, min_qty=2):
    value = 0
    for item in items:
        if item['qty'] >= min_qty:
            value += item['qty'] * item['price']
    return value

print(total_stock_value(inventory, min_qty=3))"""
    exp = (
        f"1. Hàm `total_stock_value` được gọi với tham số `min_qty = 3` (ghi đè giá trị mặc định 2).\n"
        f"2. Vòng lặp duyệt qua 3 sản phẩm trong kho và chỉ tính tiền các sản phẩm có số lượng `qty >= 3`:\n"
        f"   - Laptop (qty={p1}): {'Thỏa mãn (+' + str(p1*1000) + ')' if p1 >= 3 else 'Bỏ qua vì qty < 3'}\n"
        f"   - Mouse (qty={p2}): {'Thỏa mãn (+' + str(p2*50) + ')' if p2 >= 3 else 'Bỏ qua vì qty < 3'}\n"
        f"   - Keyboard (qty={p3}): {'Thỏa mãn (+' + str(p3*80) + ')' if p3 >= 3 else 'Bỏ qua vì qty < 3'}\n"
        f"3. Tổng giá trị của các mặt hàng thỏa điều kiện là {val}."
    )
    return code, exp

def gen_med_bitwise():
    x = random.randint(3, 12)
    shift = random.randint(1, 2)
    ans = x << shift
    code = f"x = {x}\nprint(x << {shift})"
    exp = (
        f"1. Toán tử `<<` là phép dịch trái bit (Bitwise Left Shift).\n"
        f"2. Biểu diễn nhị phân của {x}: {bin(x)}.\n"
        f"3. Dịch trái {shift} bit tương đương với việc thêm {shift} số 0 vào bên phải nhị phân (tương đương nhân với 2^{shift} = {2**shift}).\n"
        f"4. Phép tính: {x} * {2**shift} = {ans}."
    )
    return code, exp

MED_GENS = [gen_med_comprehension, gen_med_dict_set, gen_med_long_class_bank, gen_med_long_inventory, gen_med_bitwise]

# ========================================================
# 🔴 3. KHÓ (HARD) - GIẢI THÍCH CHI TIẾT SÂU SẮC
# ========================================================
def gen_hard_closures():
    k = random.randint(2, 6)
    a = k * 2 + 1
    b = k * 3 + 2
    code = f"""def count_calls(func):
    calls = 0
    def wrapper(*args, **kwargs):
        nonlocal calls
        calls += 1
        return func(*args, **kwargs) + calls
    return wrapper

@count_calls
def multiply(x, y):
    return x * y

a = multiply({k}, 2)
b = multiply({k}, 3)
print(a + b)"""
    exp = (
        f"1. Decorator `count_calls` tạo một closure lưu trữ biến trạng thái `calls = 0`.\n"
        f"2. Từ khóa `nonlocal calls` cho phép hàm wrapper sửa đổi biến calls của phạm vi bên ngoài.\n"
        f"3. Lần gọi 1 `multiply({k}, 2)`: calls tăng lên 1 -> kết quả = ({k} * 2) + 1 = {a}.\n"
        f"4. Lần gọi 2 `multiply({k}, 3)`: calls tiếp tục tăng lên 2 -> kết quả = ({k} * 3) + 2 = {b}.\n"
        f"5. Cuối cùng tính tổng: a + b = {a} + {b} = {a + b}."
    )
    return code, exp

def gen_hard_linked_list():
    v1, v2, v3 = random.randint(10, 30), random.randint(40, 60), random.randint(70, 90)
    ans = v2 + 1
    code = f"""class Node:
    def __init__(self, val, next=None):
        self.val = val
        self.next = next

class Stack:
    def __init__(self):
        self.top = None
        self.size = 0

    def push(self, val):
        self.top = Node(val, self.top)
        self.size += 1

    def pop(self):
        if not self.top:
            return None
        res = self.top.val
        self.top = self.top.next
        self.size -= 1
        return res

s = Stack()
s.push({v1})
s.push({v2})
s.push({v3})
_ = s.pop()
print(s.pop() + s.size)"""
    exp = (
        f"1. Cài đặt Ngăn xếp (Stack) theo nguyên lý vào sau ra trước (LIFO):\n"
        f"   - Lần lượt push: {v1} -> {v2} -> {v3}. Đỉnh ngăn xếp (top) là Node({v3}), size = 3.\n"
        f"2. Lệnh `_ = s.pop()` đầu tiên: Lấy Node đỉnh ({v3}) ra khỏi stack, size giảm còn 2.\n"
        f"3. Lệnh `s.pop()` thứ hai: Lấy tiếp Node({v2}) ra khỏi stack, size tiếp tục giảm còn 1.\n"
        f"4. Phép cộng: giá trị pop ({v2}) + size hiện tại ({1}) = {ans}."
    )
    return code, exp

def gen_hard_matrix():
    a, b, c, d = random.randint(1, 5), random.randint(1, 5), random.randint(1, 5), random.randint(1, 5)
    ans = c * 10 + b
    code = f"""matrix = [
    [{a}, {b}],
    [{c}, {d}]
]

def rotate_90(m):
    n = len(m)
    res = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            res[j][n - 1 - i] = m[i][j]
    return res

rotated = rotate_90(matrix)
print(rotated[0][0] * 10 + rotated[1][1])"""
    exp = (
        f"1. Thuật toán xoay ma trận vuông 90 độ theo chiều kim đồng hồ dùng công thức: `res[j][n - 1 - i] = m[i][j]`.\n"
        f"2. Ma trận ban đầu: [[{a}, {b}], [{c}, {d}]].\n"
        f"3. Sau khi xoay 90 độ, ma trận mới trở thành: [[{c}, {a}], [{d}, {b}]].\n"
        f"4. Ta có `rotated[0][0] = {c}` và `rotated[1][1] = {b}`.\n"
        f"5. Biểu thức: {c} * 10 + {b} = {ans}."
    )
    return code, exp

def gen_hard_traps():
    t = random.choice([1, 2, 3, 4, 5])
    if t == 1:
        k = random.randint(2, 6)
        code = f"def add_item(x, lst=[]):\n    lst.append(x)\n    return lst\nadd_item(1)\nprint(add_item({k}))"
        exp = (
            f"1. Bẫy Tham số Mặc định Khả biến (Mutable Default Argument):\n"
            f"2. Trong Python, giá trị mặc định `lst=[]` chỉ được tạo đúng 1 lần duy nhất khi hàm được biên dịch (def), chứ không tạo mới mỗi lần gọi.\n"
            f"3. Lần gọi 1 `add_item(1)`: Thêm 1 vào lst -> lst = [1].\n"
            f"4. Lần gọi 2 `add_item({k})`: Dùng lại chính danh sách đó và thêm {k} -> lst = [1, {k}].\n"
            f"5. Kết quả in ra là [1, {k}]."
        )
    elif t == 2:
        code = "print(0.1 + 0.2 == 0.3)"
        exp = (
            f"1. Chuẩn biểu diễn số thực dấu phẩy động nhị phân IEEE 754:\n"
            f"2. Các số thập phân vô hạn tuần hoàn trong hệ nhị phân như 0.1 và 0.2 không thể biểu diễn tuyệt đối chính xác trong bộ nhớ máy tính.\n"
            f"3. Khi cộng lại: 0.1 + 0.2 = 0.30000000000000004.\n"
            f"4. Do đó phép so sánh bằng `0.30000000000000004 == 0.3` trả về kết quả False."
        )
    elif t == 3:
        code = "print(round(2.5), round(3.5))"
        exp = (
            f"1. Python 3 áp dụng quy tắc làm tròn Bankers Rounding (làm tròn đến số chẵn gần nhất):\n"
            f"2. Khi phần thập phân chính xác là .5, số sẽ được làm tròn về số nguyên chẵn gần nhất:\n"
            f"   - 2.5 nằm giữa 2 và 3 -> số chẵn là 2, nên làm tròn thành 2.\n"
            f"   - 3.5 nằm giữa 3 và 4 -> số chẵn là 4, nên làm tròn thành 4.\n"
            f"3. Kết quả xuất ra màn hình là: 2 4."
        )
    elif t == 4:
        code = "print(isinstance(True, int), type(True) is int)"
        exp = (
            f"1. Trong ngôn ngữ Python, lớp `bool` kế thừa trực tiếp từ lớp `int` (True có giá trị số là 1, False là 0).\n"
            f"2. Hàm `isinstance(obj, Class)` kiểm tra cả tính kế thừa (inheritance), vì bool là con của int nên trả về True.\n"
            f"3. Ngược lại, so sánh danh tính chính xác `type(True) is int` so sánh kiểu dữ liệu thuần túy (type(True) là bool, không phải int) nên trả về False.\n"
            f"4. Kết quả in ra là: True False."
        )
    else:
        code = "d = {True: 'yes', 1: 'no', 1.0: 'maybe'}\nprint(len(d), d[1])"
        exp = (
            f"1. Trong Python: `True == 1 == 1.0` trả về True, và cả 3 giá trị đều có cùng mã băm: `hash(True) == hash(1) == hash(1.0)`.\n"
            f"2. Dictionary xác định khóa dựa trên hash và phép so sánh bằng (==). Vì thế, cả 3 phần tử này được xem là CÙNG MỘT KEY (Key Collision).\n"
            f"3. Khóa sau sẽ ghi đè giá trị của khóa trước: 'yes' -> 'no' -> 'maybe'.\n"
            f"4. Do đó từ điển chỉ có độ dài `len(d) = 1` và giá trị tại key 1 là 'maybe'. Kết quả: 1 maybe."
        )
    return code, exp

HARD_GENS = [gen_hard_closures, gen_hard_linked_list, gen_hard_matrix, gen_hard_traps]

DIFFICULTY_MAP = {
    "easy": EASY_GENS,
    "medium": MED_GENS,
    "hard": HARD_GENS,
    "random": EASY_GENS + MED_GENS + HARD_GENS
}

def generate_unique_question(difficulty="random", max_retries=150):
    diff_key = difficulty.lower()
    if diff_key not in DIFFICULTY_MAP:
        diff_key = "random"

    gens = DIFFICULTY_MAP[diff_key]

    for _ in range(max_retries):
        gen_func = random.choice(gens)
        code, explanation = gen_func()

        if is_code_seen(code):
            continue

        local_scope = {}
        old_stdout = sys.stdout
        redirected_output = io.StringIO()
        try:
            sys.stdout = redirected_output
            exec(code, {}, local_scope)
            sys.stdout = old_stdout
            correct_output = redirected_output.getvalue().strip()
        except Exception:
            sys.stdout = old_stdout
            continue

        if not correct_output:
            continue

        mark_code_seen(code, diff_key)

        distractors = set()

        if correct_output.isdigit() or (correct_output.startswith("-") and correct_output[1:].isdigit()):
            val = int(correct_output)
            distractors.add(str(val + 1))
            distractors.add(str(val - 1))
            distractors.add(str(val + 5))
            distractors.add(str(val * 2))
            distractors.add(str(val // 2 if val != 0 else 7))
        elif correct_output in ["True", "False"]:
            distractors.add("False" if correct_output == "True" else "True")
            distractors.add("None")
            distractors.add("SyntaxError")
        elif "True" in correct_output and "False" in correct_output:
            distractors.add("True True")
            distractors.add("False False")
            distractors.add("False True" if correct_output == "True False" else "True False")
        elif correct_output.startswith("[") and correct_output.endswith("]"):
            distractors.add(f"[{correct_output[1:-1]}, None]")
            distractors.add("[]")
            distractors.add("IndexError: list index out of range")
        elif correct_output.startswith("(") and correct_output.endswith(")"):
            distractors.add("()")
            distractors.add("(None, None)")
        else:
            distractors.add(correct_output[::-1])
            distractors.add(correct_output.upper())
            distractors.add("None")
            distractors.add("TypeError")

        common_traps = ["TypeError", "ValueError", "SyntaxError", "IndexError", "None", "0", "1", "[]"]
        for trap in common_traps:
            if trap != correct_output:
                distractors.add(trap)

        distractors.discard(correct_output)
        chosen_distractors = random.sample(list(distractors), min(3, len(distractors)))

        i = 1
        while len(chosen_distractors) < 3:
            fake = f"Result_{i}"
            if fake != correct_output and fake not in chosen_distractors:
                chosen_distractors.append(fake)
            i += 1

        options = chosen_distractors + [correct_output]
        random.shuffle(options)

        correct_index = options.index(correct_output)
        labels = ["A", "B", "C", "D"]
        correct_label = labels[correct_index]

        return {
            "difficulty": diff_key,
            "code": code,
            "explanation": explanation,
            "options": {
                "A": options[0],
                "B": options[1],
                "C": options[2],
                "D": options[3],
            },
            "correct_label": correct_label,
            "correct_answer": correct_output
        }

    fallback_code = f"print({random.randint(10, 99)} + {random.randint(10, 99)})"
    ans = str(eval(fallback_code.replace("print(", "").rstrip(")")))
    return {
        "difficulty": diff_key,
        "code": fallback_code,
        "explanation": "1. Thực hiện phép toán cộng hai số nguyên căn bản.\n2. In kết quả trực tiếp ra màn hình console.",
        "options": {"A": ans, "B": str(int(ans) + 1), "C": str(int(ans) - 1), "D": str(int(ans) * 2)},
        "correct_label": "A",
        "correct_answer": ans
    }

if __name__ == "__main__":
    for d in ["easy", "medium", "hard"]:
        q = generate_unique_question(d)
        print(f"\n--- MODE {d.upper()} ---")
        print("Code:\n" + q["code"])
        print(f"Answer: {q['correct_label']} ({q['correct_answer']})")
        print("Explanation test ok (has len:", len(q['explanation']), ")")

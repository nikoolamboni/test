import sqlite3
from datetime import datetime
from persiantools.jdatetime import JalaliDate
from plyer import notification
import tkinter as tk
from tkinter import messagebox

def create_food_table(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS foods (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            expiry_date TEXT NOT NULL
        )
    ''')
    conn.commit()

def add_food_to_table(conn, food_name, expiry_date_jalali):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO foods (name, expiry_date)
        VALUES (?, ?)
    ''', (food_name, expiry_date_jalali))
    conn.commit()

def get_all_foods(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, expiry_date FROM foods')
    return cursor.fetchall()

def show_notification(food_name, expiry_date_jalali):
    notification_title = "تاریخ انقضای مواد غذایی"
    notification_text = f"{food_name} منقضی شده است! تاریخ انقضا: {expiry_date_jalali}"
    notification.notify(
        title=notification_title,
        message=notification_text,
        app_name="Food Expiry App"
    )

def jalali_to_gregorian(jalali_date_str):
    jalali_date_parts = jalali_date_str.split('/')
    if len(jalali_date_parts) != 3:
        print("فرمت تاریخ ورودی نادرست است. لطفاً از فرمت 1402/5/16 استفاده کنید.")
        return None

    year = int(jalali_date_parts[0])
    month = int(jalali_date_parts[1])
    day = int(jalali_date_parts[2])

    jalali_date = JalaliDate(year, month, day)
    gregorian_date = jalali_date.to_gregorian()
    return gregorian_date.strftime("%Y-%m-%d")

def edit_food_name(conn, food_name, new_name):
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE foods
        SET name = ?
        WHERE name = ?
    ''', (new_name, food_name))
    conn.commit()

def edit_food_expiry_date(conn, food_name, new_expiry_date_jalali):
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE foods
        SET expiry_date = ?
        WHERE name = ?
    ''', (new_expiry_date_jalali, food_name))
    conn.commit()

def delete_food(conn, food_name):
    cursor = conn.cursor()
    cursor.execute('DELETE FROM foods WHERE name = ?', (food_name,))
    conn.commit()

def check_expired_foods(conn):
    today_gregorian = datetime.now().strftime("%Y-%m-%d")
    expired_foods = []

    foods = get_all_foods(conn)
    for food_id, food_name, expiry_date_jalali_str in foods:
        expiry_date_gregorian_str = jalali_to_gregorian(expiry_date_jalali_str)

        if expiry_date_gregorian_str <= today_gregorian:
            expired_foods.append((food_name, expiry_date_jalali_str))

    return expired_foods

def check_upcoming_expiries(conn, days, upcoming_days):
    today_gregorian = datetime.now().strftime("%Y-%m-%d")
    upcoming_expiries = []

    foods = get_all_foods(conn)
    for food_id, food_name, expiry_date_jalali_str in foods:
        expiry_date_gregorian_str = jalali_to_gregorian(expiry_date_jalali_str)

        if expiry_date_gregorian_str > today_gregorian:
            expiry_date_gregorian = datetime.strptime(expiry_date_gregorian_str, "%Y-%m-%d")
            days_until_expiry = (expiry_date_gregorian - datetime.now()).days

            if upcoming_days[0] <= days_until_expiry <= upcoming_days[1]:
                upcoming_expiries.append((food_name, expiry_date_jalali_str, days_until_expiry))

    return upcoming_expiries

def add_food():
    food_name = food_name_entry.get()
    expiry_date_jalali_str = expiry_date_entry.get()

    if not food_name or not expiry_date_jalali_str:
        messagebox.showerror("خطا", "لطفاً نام ماده غذایی و تاریخ انقضا را وارد کنید.")
    elif food_name in [food[1] for food in get_all_foods(conn)]:
        messagebox.showerror("خطا", f"ماده غذایی با نام '{food_name}' از قبل وجود دارد.")
    else:
        expiry_date_gregorian_str = jalali_to_gregorian(expiry_date_jalali_str)

        if expiry_date_gregorian_str is None:
            messagebox.showerror("خطا", "فرمت تاریخ وارد شده نادرست است. لطفاً از فرمت 1402/5/16 استفاده کنید.")
        else:
            add_food_to_table(conn, food_name, expiry_date_jalali_str)
            food_name_entry.delete(0, tk.END)
            expiry_date_entry.delete(0, tk.END)
            messagebox.showinfo("موفقیت", f"{food_name} به لیست مواد غذایی اضافه شد.")

def check_expired():
    expired_foods = check_expired_foods(conn)
    if expired_foods:
        expired_foods_str = "\n".join([f"{food_name} منقضی شده است! تاریخ انقضا: {expiry_date_jalali}" for food_name, expiry_date_jalali in expired_foods])
        messagebox.showerror("مواد غذایی منقضی", expired_foods_str)
        for food_name, expiry_date_jalali in expired_foods:
            show_notification(food_name, expiry_date_jalali)
    else:
        messagebox.showinfo("مواد غذایی منقضی", "هیچ ماده غذایی‌ای منقضی نشده است.")

def edit_name():
    food_name_to_edit = food_name_to_edit_entry_name.get()
    new_name = new_name_entry_name.get()

    if not food_name_to_edit or not new_name:
        messagebox.showerror("خطا", "لطفاً نام ماده غذایی و نام جدید را وارد کنید.")
    elif food_name_to_edit not in [food[1] for food in get_all_foods(conn)]:
        messagebox.showerror("خطا", "ماده غذایی با این نام وجود ندارد.")
    else:
        edit_food_name(conn, food_name_to_edit, new_name)
        food_name_to_edit_entry_name.delete(0, tk.END)
        new_name_entry_name.delete(0, tk.END)
        messagebox.showinfo("موفقیت", f"نام ماده غذایی با نام '{food_name_to_edit}' ویرایش شد.")

def edit_expiry_date():
    food_name_to_edit = food_name_to_edit_entry.get()
    new_expiry_date_jalali_str = new_expiry_date_entry.get()
    expiry_date_gregorian_str = jalali_to_gregorian(new_expiry_date_jalali_str)

    if not food_name_to_edit or not new_expiry_date_jalali_str:
        messagebox.showerror("خطا", "لطفاً نام ماده غذایی و تاریخ جدید انقضا را وارد کنید.")
    elif food_name_to_edit not in [food[1] for food in get_all_foods(conn)]:
        messagebox.showerror("خطا", "ماده غذایی با این نام وجود ندارد.")
    elif expiry_date_gregorian_str is None:
        messagebox.showerror("خطا", "فرمت تاریخ وارد شده نادرست است. لطفاً از فرمت 1402/5/16 استفاده کنید.")
    else:
        existing_expiry_date_gregorian_str = None
        for food_id, food_name, expiry_date_jalali in get_all_foods(conn):
            if food_name == food_name_to_edit:
                existing_expiry_date_gregorian_str = jalali_to_gregorian(expiry_date_jalali)
                break

        today_gregorian = datetime.now().strftime("%Y-%m-%d")
        if existing_expiry_date_gregorian_str is not None:
            if expiry_date_gregorian_str > existing_expiry_date_gregorian_str:
                edit_food_expiry_date(conn, food_name_to_edit, new_expiry_date_jalali_str)

                if expiry_date_gregorian_str > today_gregorian:
                    show_notification(food_name_to_edit, new_expiry_date_jalali_str)

                messagebox.showinfo("موفقیت", f"تاریخ انقضای ماده غذایی با نام '{food_name_to_edit}' ویرایش شد.")
            else:
                messagebox.showerror("خطا", "تاریخ انقضای جدید باید بعد از تاریخ فعلی باشد.")
                edit_food_expiry_date(conn, food_name_to_edit, new_expiry_date_jalali_str)
        else:
            messagebox.showerror("خطا", "خطایی رخ داد. تاریخ انقضای فعلی پیدا نشد.")
        
def delete():
    food_name_to_delete = food_name_to_delete_entry.get()

    if not food_name_to_delete:
        messagebox.showerror("خطا", "لطفاً نام ماده غذایی را برای حذف وارد کنید.")
    elif food_name_to_delete not in [food[1] for food in get_all_foods(conn)]:
        messagebox.showerror("خطا", "ماده غذایی با این نام وجود ندارد.")
    else:
        delete_food(conn, food_name_to_delete)
        food_name_to_delete_entry.delete(0, tk.END)
        messagebox.showinfo("موفقیت", f"ماده غذایی با نام '{food_name_to_delete}' حذف شد.")

def show_upcoming_expiries(upcoming_days):
    upcoming_expiries = check_upcoming_expiries(conn, 15, upcoming_days)
    if upcoming_expiries:
        upcoming_expiries_str = "\n".join([f"{food_name} - تاریخ انقضا: {expiry_date_jalali} - تا {days_until_expiry+1} روز دیگر" for food_name, expiry_date_jalali, days_until_expiry in upcoming_expiries])
        messagebox.showinfo(f"تاریخ انقضا بین {upcoming_days[0]} تا {upcoming_days[1]} روز", upcoming_expiries_str)
    else:
        messagebox.showinfo(f"تاریخ انقضا بین {upcoming_days[0]} تا {upcoming_days[1]} روز", "مواد غذایی با تاریخ انقضای بین این بازه وجود ندارد.")

conn = sqlite3.connect('food_inventory.db')
create_food_table(conn)

root = tk.Tk()
root.title("برنامه مدیریت مواد غذایی")
root.geometry("700x400")

root.attributes('-alpha', 0.96)

background_image = tk.PhotoImage(file="icon.png")

background_label = tk.Label(root, image=background_image)
background_label.place(relwidth=1, relheight=1)  # تنظیم اندازه تصویر به اندازه پنجره


def list_all_foods():
    foods = get_all_foods(conn)
    if foods:
        food_list_str = "\n".join([f"{food_name} - تاریخ انقضا: {expiry_date_jalali}" for _, food_name, expiry_date_jalali in foods])
        messagebox.showinfo("لیست مواد غذایی", food_list_str)
    else:
        messagebox.showinfo("لیست مواد غذایی", "هیچ ماده غذایی‌ای موجود نیست.")
        

frame8 = tk.Frame(root)
frame8.pack()
list_all_button = tk.Button(frame8, text="نمایش لیست تمام مواد غذایی", command=list_all_foods)
list_all_button.pack()



# ایجاد ویجت‌ها
frame1 = tk.Frame(root)
frame1.pack()
label1 = tk.Label(frame1, text=" : نام ماده غذایی ")
label1.pack(side=tk.RIGHT , padx=10)
food_name_entry = tk.Entry(frame1)
food_name_entry.pack(side=tk.RIGHT, padx=10)
label2 = tk.Label(frame1, text=": (1402/5/16) تاریخ انقضا ")
label2.pack(side=tk.RIGHT)
expiry_date_entry = tk.Entry(frame1)
expiry_date_entry.pack(side=tk.RIGHT)
add_button = tk.Button(frame1, text="اضافه کردن ماده غذایی", command=add_food)
add_button.pack(side=tk.RIGHT)

frame2 = tk.Frame(root)
frame2.pack()
check_expired_button = tk.Button(frame2, text="بررسی تاریخ مصرف", command=check_expired)
check_expired_button.pack()

frame3 = tk.Frame(root)
frame3.pack()
label3 = tk.Label(frame3, text=" : نام ماده غذایی ")
label3.pack(side=tk.RIGHT)
food_name_to_edit_entry_name = tk.Entry(frame3)
food_name_to_edit_entry_name.pack(side=tk.RIGHT)
label4 = tk.Label(frame3, text=" : نام جدید ")
label4.pack(side=tk.RIGHT)
new_name_entry_name = tk.Entry(frame3)
new_name_entry_name.pack(side=tk.RIGHT)
edit_name_button = tk.Button(frame3, text="ویرایش نام ماده غذایی", command=edit_name)
edit_name_button.pack(side=tk.RIGHT)

frame4 = tk.Frame(root)
frame4.pack()
label5 = tk.Label(frame4, text=" : نام ماده غذایی ")
label5.pack(side=tk.RIGHT)
food_name_to_edit_entry = tk.Entry(frame4)
food_name_to_edit_entry.pack(side=tk.RIGHT)
label6 = tk.Label(frame4, text=": (1402/5/16) تاریخ انقضا ")
label6.pack(side=tk.RIGHT)
new_expiry_date_entry = tk.Entry(frame4)
new_expiry_date_entry.pack(side=tk.RIGHT)
edit_expiry_date_button = tk.Button(frame4, text="ویرایش تاریخ انقضا", command=edit_expiry_date)
edit_expiry_date_button.pack(side=tk.RIGHT)

frame5 = tk.Frame(root)
frame5.pack()
label7 = tk.Label(frame5, text=" : نام ماده غذایی ")
label7.pack(side=tk.RIGHT)
food_name_to_delete_entry = tk.Entry(frame5)
food_name_to_delete_entry.pack(side=tk.RIGHT)
delete_button = tk.Button(frame5, text="حذف ماده غذایی", command=delete)
delete_button.pack(side=tk.RIGHT)

frame6 = tk.Frame(root)
frame6.pack()
upcoming_button1 = tk.Button(frame6, text="نمایش مواد غذایی با تاریخ انقضای 7 تا 15 روز", command=lambda: show_upcoming_expiries((7, 15)))
upcoming_button1.pack(side=tk.RIGHT)
upcoming_button2 = tk.Button(frame6, text="نمایش مواد غذایی با تاریخ انقضای 15 تا 30 روز", command=lambda: show_upcoming_expiries((15, 30)))
upcoming_button2.pack(side=tk.RIGHT)

frame7 = tk.Frame(root)
frame7.pack()
exit_button = tk.Button(frame7, text="خروج", command=root.destroy)
exit_button.pack()

root.mainloop()

conn.close()

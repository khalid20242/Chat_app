import sqlite3
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import re
import time
from tkcalendar import Calendar
import sqlite3
from tkinter import Toplevel
import socket


def create_doctor_table():
    conn = sqlite3.connect('users.db')  # الاتصال بقاعدة البيانات
    c = conn.cursor()

    # إنشاء جدول الأطباء إذا لم يكن موجودًا
    c.execute('''
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # إضافة حسابات افتراضية
    doctors = [
        ('Dr. John Doe', 'john.doe@example.com', 'password123'),
        ('Dr. Jane Smith', 'jane.smith@example.com', 'securepass456'),
        ('Dr. Emily Davis', 'emily.davis@example.com', 'mypassword789'),
    ]

    for doctor in doctors:
        try:
            c.execute('INSERT INTO doctors (name, email, password) VALUES (?, ?, ?)', doctor)
        except sqlite3.IntegrityError:
            pass  # تجاهل الخطأ إذا كان الحساب موجودًا بالفعل

    conn.commit()
    conn.close()


# دالة لإنشاء قاعدة البيانات
def create_database():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    # Create users table if not exists
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            email TEXT UNIQUE,
            password TEXT
        )
    ''')

    # Create appointments table if not exists
    c.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            doctor_name TEXT,
            appointment_time TEXT,
            appointment_datetime TEXT,  -- New column for storing both date and time
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    # Check if the new column exists, if not, add it
    try:
        c.execute('''ALTER TABLE appointments ADD COLUMN appointment_datetime TEXT''')
    except sqlite3.OperationalError:
        # If the column already exists, ignore the error
        pass

    conn.commit()
    conn.close()


# إعداد CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# عرض صفحة الترحيب
def show_welcome_page(root1):
    for widget in root1.winfo_children():
        widget.destroy()

    root1.configure(bg="#1e1e2f")

    welcome_frame = ctk.CTkFrame(root1, width=880, height=550, corner_radius=20, fg_color="#2c2c3d")
    welcome_frame.place(relx=0.5, rely=0.5, anchor="center")

    try:
        img = Image.open("care22.png")
        img_resized = img.resize((150, 150))
        img_ctk = ctk.CTkImage(light_image=img_resized, dark_image=img_resized, size=(150, 150))

        image_frame = ctk.CTkFrame(welcome_frame, width=160, height=160, corner_radius=15, fg_color="#3e3e54")
        image_frame.place(relx=0.5, rely=0.2, anchor="center")
        image_label = ctk.CTkLabel(image_frame, image=img_ctk, text="")
        image_label.pack(padx=5, pady=5)

    except Exception as e:
        error_label = ctk.CTkLabel(welcome_frame, text=f"Error loading image: {e}", text_color="red")
        error_label.place(x=450, y=200)

    welcome_label = ctk.CTkLabel(
        welcome_frame,
        text="Welcome to Care App!",
        font=("Arial", 32, "bold"),
        text_color="#ffffff"
    )
    welcome_label.place(relx=0.5, rely=0.45, anchor="center")

    description_label = ctk.CTkLabel(
        welcome_frame,
        text="We are delighted to have you here and excited to accompany you on your journey.",
        font=("Arial", 16),
        text_color="#a1a1b3",
        wraplength=700,
        justify="left"
    )
    description_label.place(relx=0.5, rely=0.65, anchor="center")

    start_button = ctk.CTkButton(
        welcome_frame,
        text="Start",
        width=250,
        height=50,
        fg_color="#4e9eff",
        text_color="#ffffff",
        corner_radius=15,
        hover_color="#5ab3ff",
        command=lambda: open_login_interface(welcome_frame, root1)
    )
    start_button.place(relx=0.5, rely=0.85, anchor="center")


# دالة لعرض واجهة الطبيب الرئيسية (Dashboard)
def show_doctor_dashboard(root):
    # مسح جميع العناصر الموجودة
    for widget in root.winfo_children():
        widget.destroy()

    # إنشاء إطار لوحة التحكم
    dashboard_frame = ctk.CTkFrame(root, width=880, height=550, corner_radius=20, fg_color="#2c2c3d")
    dashboard_frame.place(relx=0.5, rely=0.5, anchor="center")

    # عنوان لوحة التحكم
    title_label = ctk.CTkLabel(
        dashboard_frame,
        text="Doctor Dashboard",
        font=("Arial", 24, "bold"),
        text_color="#ffffff"
    )
    title_label.place(relx=0.5, rely=0.05, anchor="center")

    # زر لعرض المواعيد داخل نافذة جديدة
    appointments_button = ctk.CTkButton(
        dashboard_frame,
        text="View Appointments",  # نص الزر
        width=300,
        height=50,
        fg_color="#4e9eff",
        text_color="#ffffff",
        corner_radius=10,
        hover_color="#5ab3ff",
        command=lambda: open_appointments_window()  # فتح نافذة المواعيد بشكل مستقل
    )
    appointments_button.place(relx=0.5, rely=0.3, anchor="center")

    # زر لفتح صفحة الدردشة
    chat_button = ctk.CTkButton(
        dashboard_frame,
        text="Chat",  # نص الزر
        width=300,
        height=50,
        fg_color="#4e9eff",
        text_color="#ffffff",
        corner_radius=10,
        hover_color="#5ab3ff",
        command=lambda: create_chat_interface(root)
    )
    chat_button.place(relx=0.5, rely=0.45, anchor="center")

    # زر الخروج
    logout_button = ctk.CTkButton(
        dashboard_frame,
        text="Logout",
        width=150,
        height=40,
        fg_color="#ff5a5a",
        text_color="#ffffff",
        corner_radius=10,
        hover_color="#ff7777",
        command=lambda: show_welcome_page(root)  # العودة إلى صفحة الترحيب
    )
    logout_button.place(relx=0.5, rely=0.92, anchor="center")


# دالة لفتح نافذة المواعيد بشكل منفصل
def open_appointments_window():
    # إنشاء نافذة جديدة لعرض المواعيد
    appointments_window = Toplevel()
    appointments_window.title("Appointments")
    appointments_window.geometry("880x550")

    # إضافة إطار لعرض المواعيد
    appointments_frame = ctk.CTkScrollableFrame(appointments_window, width=880, height=550, corner_radius=20,
                                                fg_color="#2c2c3d")
    appointments_frame.pack(fill="both", expand=True)

    # عنوان نافذة المواعيد
    title_label = ctk.CTkLabel(
        appointments_frame,
        text="Appointments",
        font=("Arial", 24, "bold"),
        text_color="#ffffff"
    )
    title_label.place(relx=0.5, rely=0.05, anchor="center")

    # جلب المواعيد من قاعدة البيانات
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute('''
            SELECT users.name, appointments.id, appointments.appointment_datetime, appointments.status
            FROM appointments
            JOIN users ON appointments.user_id = users.id
            ORDER BY appointments.appointment_datetime
        ''')
        appointments = c.fetchall()
    finally:
        conn.close()

    # عرض العناوين كجدول
    header_frame = ctk.CTkFrame(appointments_frame, fg_color="#4e4e6a")
    header_frame.pack(fill="x", padx=5, pady=5)

    ctk.CTkLabel(header_frame, text="Patient Name", font=("Arial", 14, "bold"), text_color="#ffffff").grid(row=0,
                                                                                                           column=0,
                                                                                                           padx=10)
    ctk.CTkLabel(header_frame, text="Appointment Date & Time", font=("Arial", 14, "bold"), text_color="#ffffff").grid(
        row=0, column=1, padx=10)
    ctk.CTkLabel(header_frame, text="Status", font=("Arial", 14, "bold"), text_color="#ffffff").grid(row=0, column=2,
                                                                                                     padx=10)
    ctk.CTkLabel(header_frame, text="Action", font=("Arial", 14, "bold"), text_color="#ffffff").grid(row=0, column=3,
                                                                                                     padx=10)

    # عرض المواعيد
    if appointments:
        for index, (user_name, appointment_id, appointment_datetime, status) in enumerate(appointments):
            row_color = "#3e3e52" if index % 2 == 0 else "#2c2c3d"
            row_frame = ctk.CTkFrame(appointments_frame, fg_color=row_color)
            row_frame.pack(fill="x", padx=5, pady=2)

            ctk.CTkLabel(row_frame, text=user_name, font=("Arial", 12), text_color="#ffffff").grid(row=0, column=0,
                                                                                                   padx=10)
            ctk.CTkLabel(row_frame, text=appointment_datetime, font=("Arial", 12), text_color="#ffffff").grid(row=0,
                                                                                                              column=1,
                                                                                                              padx=10)
            ctk.CTkLabel(row_frame, text=status, font=("Arial", 12), text_color="#ffffff").grid(row=0, column=2,
                                                                                                padx=10)

            # زر إتمام الموعد
            complete_button = ctk.CTkButton(
                row_frame,
                text="Complete",
                width=150,
                height=35,
                fg_color="#4CAF50",
                text_color="#ffffff",
                corner_radius=10,
                hover_color="#66BB6A",
                font=("Arial", 14, "bold"),
                command=lambda id=appointment_id: mark_appointment_complete(id, appointments_window)
                # استدعاء دالة إتمام الموعد
            )
            complete_button.grid(row=0, column=3, padx=10, pady=5)
    else:
        no_appointments_label = ctk.CTkLabel(
            appointments_frame,
            text="No appointments found.",
            font=("Arial", 16),
            text_color="#a1a1b3"
        )
        no_appointments_label.pack(pady=20)


# دالة لإتمام الموعد وتحديث الحالة في قاعدة البيانات
def mark_appointment_complete(appointment_id, appointments_window):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        # تحديث حالة الموعد إلى "مكتمل"
        c.execute('''
            UPDATE appointments
            SET status = 'Completed'
            WHERE id = ?
        ''', (appointment_id,))
        conn.commit()
        messagebox.showinfo("Success", "Appointment marked as completed!")
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"Could not update appointment: {e}")
    finally:
        conn.close()

    # إعادة تحميل المواعيد لتحديث الحالة
    appointments_window.destroy()  # إغلاق النافذة الحالية
    open_appointments_window()  # فتح نافذة المواعيد مرة أخرى لتحديث الحالة


# دالة لإتمام الموعد


def update_database_schema():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute('''ALTER TABLE appointments ADD COLUMN status TEXT DEFAULT 'Pending' ''')
    except sqlite3.OperationalError:
        pass  # إذا كان العمود موجودًا بالفعل، تجاهل الخطأ
    conn.commit()
    conn.close()


# فتح واجهة تسجيل الدخول
def open_login_interface(welcome_frame, root3):
    if welcome_frame:
        welcome_frame.pack_forget()

    login_frame = ctk.CTkFrame(root3, width=880, height=550, corner_radius=20, fg_color="#2c2c3d")
    login_frame.place(relx=0.5, rely=0.5, anchor="center")

    try:
        img = Image.open("c2.jpg")
        img_resized = img.resize((380, 380))
        img_ctk = ctk.CTkImage(light_image=img_resized, dark_image=img_resized, size=(380, 380))

        image_outer_frame = ctk.CTkFrame(login_frame, width=400, height=400, corner_radius=20, fg_color="#3a3a4a")
        image_outer_frame.place(x=460, y=50)

        image_inner_frame = ctk.CTkFrame(image_outer_frame, width=380, height=380, corner_radius=15, fg_color="#ffffff")
        image_inner_frame.place(relx=0.5, rely=0.5, anchor="center")

        image_label = ctk.CTkLabel(image_inner_frame, image=img_ctk, text="")
        image_label.pack(padx=10, pady=10)

    except Exception as e:
        error_label = ctk.CTkLabel(login_frame, text=f"Error loading image: {e}", text_color="red")
        error_label.place(x=470, y=50)

    title_label = ctk.CTkLabel(
        login_frame,
        text="Login to Your Account",
        font=("Arial", 24, "bold"),
        text_color="#ffffff"
    )
    title_label.place(x=30, y=30)

    email_entry = ctk.CTkEntry(
        login_frame,
        placeholder_text="Email",
        width=300,
        height=40,
        corner_radius=10
    )
    email_entry.place(x=30, y=100)

    password_entry = ctk.CTkEntry(
        login_frame,
        placeholder_text="Password",
        width=300,
        height=40,
        show="*",
        corner_radius=10
    )
    password_entry.place(x=30, y=160)

    def login():
        email = email_entry.get()
        password = password_entry.get()
        if email and password:
            conn = sqlite3.connect('users.db')
            c = conn.cursor()

            # التحقق من صحة بيانات الدخول
            c.execute('SELECT id, name FROM users WHERE email = ? AND password = ?', (email, password))
            user = c.fetchone()

            if user:
                global current_user_id
                current_user_id = user[0]  # تخزين معرف المستخدم
                messagebox.showinfo("Login", f"Welcome back, {user[1]}!")  # user[1] هو الاسم
                show_welcome_user_page(root3)  # الانتقال إلى صفحة الترحيب بعد تسجيل الدخول
            else:
                messagebox.showerror("Login Failed", "Invalid email or password.")
            conn.close()
        else:
            messagebox.showwarning("Login", "Please enter both email and password.")

    login_button = ctk.CTkButton(
        login_frame,
        text="Sign In",
        width=300,
        height=40,
        fg_color="#4e9eff",
        text_color="#ffffff",
        corner_radius=10,
        hover_color="#5ab3ff",
        command=login
    )
    login_button.place(x=30, y=220)

    def create_account():
        open_create_account_interface(login_frame, root3)

    create_account_button = ctk.CTkButton(
        login_frame,
        text="Create an Account",
        width=300,
        height=40,
        fg_color="#ff9e00",
        text_color="#ffffff",
        corner_radius=10,
        hover_color="#ffb733",
        command=create_account
    )
    create_account_button.place(x=30, y=270)

    def go_back():
        login_frame.pack_forget()
        show_welcome_page(root3)

    doctor_login_button = ctk.CTkButton(
        login_frame,
        text="Doctor Login",
        width=100,
        height=40,
        fg_color="#ffffff",
        text_color="#000000",
        corner_radius=10,
        hover_color="#e6e6e6",
        command=lambda: open_doctor_login_interface2(root3)  # استدعاء دالة فتح واجهة تسجيل دخول الأطباء
    )
    doctor_login_button.place(x=30, y=330)

    def open_doctor_login_interface2(root4):
        # مسح جميع العناصر الموجودة في النافذة
        for widget in root4.winfo_children():
            widget.destroy()

        # إنشاء إطار تسجيل دخول الأطباء
        doctor_login_frame = ctk.CTkFrame(root4, width=880, height=550, corner_radius=20, fg_color="#2c2c3d")
        doctor_login_frame.place(relx=0.5, rely=0.5, anchor="center")

        # عنوان صفحة تسجيل دخول الأطباء
        title_label1 = ctk.CTkLabel(
            doctor_login_frame,
            text="Doctor Login",
            font=("Arial", 24, "bold"),
            text_color="#ffffff"
        )
        title_label1.place(relx=0.5, rely=0.1, anchor="center")

        # إدخال البريد الإلكتروني
        email_entry1 = ctk.CTkEntry(
            doctor_login_frame,
            placeholder_text="Email",
            width=300,
            height=40,
            corner_radius=10
        )
        email_entry1.place(relx=0.5, rely=0.3, anchor="center")

        # إدخال كلمة المرور
        password_entry1 = ctk.CTkEntry(
            doctor_login_frame,
            placeholder_text="Password",
            width=300,
            height=40,
            show="*",
            corner_radius=10
        )
        password_entry1.place(relx=0.5, rely=0.4, anchor="center")

        # التحقق من بيانات تسجيل الدخول
        def doctor_login():
            email = email_entry1.get()
            password = password_entry1.get()

            if email and password:
                # فتح اتصال بقاعدة البيانات
                conn = sqlite3.connect('users.db')
                c = conn.cursor()

                # التحقق من بيانات الطبيب
                c.execute('SELECT id, name FROM doctors WHERE email = ? AND password = ?', (email, password))
                doctor = c.fetchone()

                if doctor:
                    messagebox.showinfo("Login Success", f"Welcome, Dr. {doctor[1]}!")
                    show_doctor_dashboard(root4)  # الانتقال إلى لوحة التحكم
                else:
                    messagebox.showerror("Login Failed", "Invalid email or password.")
                conn.close()
            else:
                messagebox.showwarning("Missing Information", "Please fill out all fields.")

        # زر تسجيل الدخول
        login_button1 = ctk.CTkButton(
            doctor_login_frame,
            text="Sign In",
            width=300,
            height=40,
            fg_color="#4e9eff",
            text_color="#ffffff",
            corner_radius=10,
            hover_color="#5ab3ff",
            command=doctor_login
        )
        login_button1.place(relx=0.5, rely=0.55, anchor="center")

        # زر العودة
        back_button1 = ctk.CTkButton(
            doctor_login_frame,
            text="Back",
            width=100,
            height=40,
            fg_color="#ffffff",
            text_color="#000000",
            corner_radius=10,
            hover_color="#e6e6e6",
            command=lambda: show_welcome_page(root4)  # العودة إلى صفحة الترحيب
        )
        back_button1.place(relx=0.5, rely=0.7, anchor="center")

    # لوحة التحكم للأطباء

    # زر العودة

    back_button3 = ctk.CTkButton(
        login_frame,
        text="Back",
        width=100,
        height=40,
        fg_color="#ffffff",
        text_color="#000000",
        corner_radius=10,
        hover_color="#e6e6e6",
        command=go_back
    )
    back_button3.place(x=30, y=390)


# فتح واجهة إنشاء حساب
def open_create_account_interface(login_frame, root6):
    login_frame.pack_forget()

    create_account_frame = ctk.CTkFrame(root6, width=880, height=550, corner_radius=20, fg_color="#2c2c3d")
    create_account_frame.place(relx=0.5, rely=0.5, anchor="center")

    title_label = ctk.CTkLabel(
        create_account_frame,
        text="Create Your Account",
        font=("Arial", 24, "bold"),
        text_color="#ffffff"
    )
    title_label.place(x=30, y=30)

    name_entry = ctk.CTkEntry(
        create_account_frame,
        placeholder_text="Name",
        width=300,
        height=40,
        corner_radius=10
    )
    name_entry.place(x=30, y=100)

    phone_entry = ctk.CTkEntry(
        create_account_frame,
        placeholder_text="Phone",
        width=300,
        height=40,
        corner_radius=10
    )
    phone_entry.place(x=30, y=160)

    email_entry = ctk.CTkEntry(
        create_account_frame,
        placeholder_text="Email",
        width=300,
        height=40,
        corner_radius=10
    )
    email_entry.place(x=30, y=220)

    password_entry = ctk.CTkEntry(
        create_account_frame,
        placeholder_text="Password",
        width=300,
        height=40,
        show="*",
        corner_radius=10
    )
    password_entry.place(x=30, y=280)

    def create_account():
        name = name_entry.get()
        phone = phone_entry.get()
        email = email_entry.get()
        password = password_entry.get()

        if name and phone and email and password:
            # التحقق من صحة البريد الإلكتروني
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                messagebox.showerror("Invalid Email", "Please enter a valid email address.")
                return

            # التحقق من صحة رقم الهاتف (يجب أن يكون 10 أرقام)
            if len(phone) != 10 or not phone.isdigit():
                messagebox.showerror("Invalid Phone", "Phone number must be 10 digits.")
                return

            # التحقق من أن البريد الإلكتروني غير موجود بالفعل
            conn = sqlite3.connect('users.db')
            c = conn.cursor()
            c.execute('SELECT * FROM users WHERE email = ?', (email,))
            user = c.fetchone()
            if user:
                messagebox.showerror("Account Exists", "An account with this email already exists.")
            else:
                c.execute('INSERT INTO users (name, phone, email, password) VALUES (?, ?, ?, ?)',
                          (name, phone, email, password))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Account created successfully!")
                open_login_interface(create_account_frame, root6)  # العودة لواجهة تسجيل الدخول بعد إنشاء الحساب
        else:
            messagebox.showwarning("Missing Information", "Please fill out all fields.")

    create_button = ctk.CTkButton(
        create_account_frame,
        text="Create Account",
        width=300,
        height=40,
        fg_color="#4e9eff",
        text_color="#ffffff",
        corner_radius=10,
        hover_color="#5ab3ff",
        command=create_account
    )
    create_button.place(x=30, y=350)

    def go_back():
        create_account_frame.pack_forget()
        open_login_interface(None, root6)

    back_button = ctk.CTkButton(
        create_account_frame,
        text="Back",
        width=100,
        height=40,
        fg_color="#ffffff",
        text_color="#000000",
        corner_radius=10,
        hover_color="#e6e6e6",
        command=go_back
    )
    back_button.place(x=30, y=420)


# صفحة الترحيب بعد التسجيل
def show_welcome_user_page(root7):
    for widget in root7.winfo_children():
        widget.destroy()

    root7.configure(bg="#1e1e2f")

    welcome_user_frame = ctk.CTkFrame(root7, width=880, height=550, corner_radius=20, fg_color="#2c2c3d")
    welcome_user_frame.place(relx=0.5, rely=0.5, anchor="center")

    welcome_label = ctk.CTkLabel(
        welcome_user_frame,
        text="Welcome to the Family!",
        font=("Arial", 32, "bold"),
        text_color="#ffffff"
    )
    welcome_label.place(relx=0.5, rely=0.3, anchor="center")

    description_label = ctk.CTkLabel(
        welcome_user_frame,
        text="You are now part of our family! Let's get started.",
        font=("Arial", 16),
        text_color="#a1a1b3",
        wraplength=700,
        justify="left"
    )
    description_label.place(relx=0.5, rely=0.5, anchor="center")

    start_button = ctk.CTkButton(
        welcome_user_frame,
        text="Start",
        width=250,
        height=50,
        fg_color="#4e9eff",
        text_color="#ffffff",
        corner_radius=15,
        hover_color="#5ab3ff",
        command=lambda: show_options_page(root7)
    )
    start_button.place(relx=0.5, rely=0.7, anchor="center")


# الدالة لعرض الصفحة الرئيسية
def show_options_page(root8):
    for widget in root8.winfo_children():
        widget.destroy()

    root8.configure(bg="#1e1e2f")

    options_frame = ctk.CTkFrame(root8, width=880, height=550, corner_radius=20, fg_color="#2c2c3d")
    options_frame.place(relx=0.5, rely=0.5, anchor="center")

    option_label = ctk.CTkLabel(
        options_frame,
        text="Choose an Option",
        font=("Arial", 24, "bold"),
        text_color="#ffffff"
    )
    option_label.place(relx=0.5, rely=0.2, anchor="center")

    # زر الخيار 1 في المنتصف
    option1_button = ctk.CTkButton(
        options_frame,
        text="Book an Appointment",
        width=300,
        height=50,
        fg_color="#4e9eff",
        text_color="#ffffff",
        corner_radius=10,
        hover_color="#5ab3ff",
        command=lambda: open_booking_page(root8)  # ربط الدالة مع النافذة الرئيسية
    )

    option1_button.place(relx=0.5, rely=0.4, anchor="center")

    # زر الخيار 2 لعرض الفحوصات
    option2_button = ctk.CTkButton(
        options_frame,
        text="View Tests",
        width=300,
        height=50,
        fg_color="#4e9eff",
        text_color="#ffffff",
        corner_radius=10,
        hover_color="#5ab3ff",
        command=lambda: show_tests(options_frame)  # ربط دالة show_tests مع الزر
    )
    option2_button.place(relx=0.5, rely=0.5, anchor="center")

    # زر الخيار 3 في المنتصف
    option3_button = ctk.CTkButton(
        options_frame,
        text="Chat",
        width=300,
        height=50,
        fg_color="#4e9eff",
        text_color="#ffffff",
        corner_radius=10,
        hover_color="#5ab3ff",
        command=lambda: create_chat_interface(root)  # استخدام الدالة بشكل صحيح
    )
    option3_button.place(relx=0.5, rely=0.6, anchor="center")

    def go_back():
        show_welcome_page(root8)

    back_button = ctk.CTkButton(
        options_frame,
        text="Back to Options",
        width=200,
        height=40,
        fg_color="#FF6347",
        text_color="white",
        corner_radius=10,
        hover_color="#FF7F7F",
        command=go_back
    )
    back_button.place(relx=0.5, rely=0.9, anchor="center")


def open_booking_page(root9):
    # مسح كل العناصر الموجودة في الصفحة الحالية
    for widget in root9.winfo_children():
        widget.destroy()

    # إنشاء الإطار الخاص بصفحة الحجز
    booking_frame = ctk.CTkFrame(root9, width=880, height=550, corner_radius=20, fg_color="#2c2c3d")
    booking_frame.place(relx=0.5, rely=0.5, anchor="center")

    # عنوان صفحة الحجز
    title_label = ctk.CTkLabel(
        booking_frame,
        text="Book an Appointment",
        font=("Arial", 24, "bold"),
        text_color="#ffffff"
    )
    title_label.place(relx=0.5, rely=0.1, anchor="center")

    # دالة لحجز الموعد
    def confirm_booking():
        doctor_name = doctor_var.get()
        appointment_time = time_entry.get()
        appointment_date = cal.get_date()

        if doctor_name == "Select a doctor" or not appointment_time:
            messagebox.showwarning("Incomplete Data", "Please select a doctor and specify a time.")
            return

        if not re.match(r"^\d{2}:\d{2}$", appointment_time):
            messagebox.showerror("Invalid Time", "Time must be in the format HH:MM.")
            return

        conn = sqlite3.connect('users.db')
        c = conn.cursor()

        # Combine the date and time
        appointment_datetime = f"{appointment_date} {appointment_time}"

        try:
            c.execute('''
                INSERT INTO appointments (user_id, doctor_name, appointment_datetime)
                VALUES (?, ?, ?)
            ''', (current_user_id, doctor_name, appointment_datetime))  # استخدام current_user_id
            conn.commit()
            messagebox.showinfo("Success", f"Appointment booked with {doctor_name} on {appointment_datetime}!")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            conn.close()

        open_booking_page(root9)

    # حقل لاختيار الطبيب
    doctor_var = ctk.StringVar(value="Select a doctor")
    doctor_dropdown = ctk.CTkOptionMenu(booking_frame, variable=doctor_var, values=["Doctor A", "Doctor B", "Doctor C"])
    doctor_dropdown.place(relx=0.5, rely=0.2, anchor="center")

    # حقل لاختيار التاريخ
    cal = Calendar(booking_frame, selectmode="day", date_pattern="yyyy-mm-dd")
    cal.place(relx=0.5, rely=0.35, anchor="center")

    # حقل لادخال الوقت
    time_entry = ctk.CTkEntry(booking_frame, placeholder_text="Enter time (HH:MM)")
    time_entry.place(relx=0.5, rely=0.55, anchor="center")

    # زر لحجز الموعد
    confirm_button = ctk.CTkButton(
        booking_frame,
        text="Confirm Appointment",
        width=300,
        height=50,
        fg_color="#4e9eff",
        text_color="#ffffff",
        corner_radius=10,
        hover_color="#5ab3ff",
        command=confirm_booking
    )
    confirm_button.place(relx=0.5, rely=0.7, anchor="center")

    # زر عرض المواعيد السابقة
    previous_appointments_button = ctk.CTkButton(
        booking_frame,
        text="View Previous Appointments",
        width=300,
        height=50,
        fg_color="#ff9e00",
        text_color="#ffffff",
        corner_radius=10,
        hover_color="#ffb733",
        command=lambda: show_previous_appointments_in_booking_page(booking_frame, root9)
    )
    previous_appointments_button.place(relx=0.5, rely=0.8, anchor="center")

    # زر العودة إلى صفحة الخيارات
    back_button = ctk.CTkButton(
        booking_frame,
        text="Back",
        width=100,
        height=40,
        fg_color="#ffffff",
        text_color="#000000",
        corner_radius=10,
        hover_color="#e6e6e6",
        command=lambda: show_options_page(root9)  # العودة إلى صفحة الخيارات
    )
    back_button.place(relx=0.5, rely=0.9, anchor="center")


def show_previous_appointments_in_booking_page(booking_frame, root10):
    for widget in booking_frame.winfo_children():
        widget.destroy()

    title_label = ctk.CTkLabel(
        booking_frame,
        text="Previous Appointments",
        font=("Arial", 24, "bold"),
        text_color="#ffffff"
    )
    title_label.place(relx=0.5, rely=0.1, anchor="center")

    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    try:
        c.execute('''
            SELECT doctor_name, appointment_datetime FROM appointments
            WHERE user_id = ?
            ORDER BY appointment_datetime
        ''', (current_user_id,))  # استخدام current_user_id
        appointments = c.fetchall()
    finally:
        conn.close()

    if not appointments:
        no_appointments_label = ctk.CTkLabel(
            booking_frame,
            text="No previous appointments found.",
            font=("Arial", 16),
            text_color="#a1a1b3"
        )
        no_appointments_label.place(relx=0.5, rely=0.5, anchor="center")
    else:
        for index, (doctor_name, appointment_datetime) in enumerate(appointments):
            appointment_label = ctk.CTkLabel(
                booking_frame,
                text=f"{index + 1}. Dr. {doctor_name} - {appointment_datetime}",
                font=("Arial", 14),
                text_color="#ffffff",
                anchor="w"
            )
            appointment_label.place(relx=0.1, rely=0.2 + (index * 0.1), anchor="w")

    # زر العودة إلى صفحة الحجز
    back_button = ctk.CTkButton(
        booking_frame,
        text="Back",
        width=100,
        height=40,
        fg_color="#ffffff",
        text_color="#000000",
        corner_radius=10,
        hover_color="#e6e6e6",
        command=lambda: open_booking_page(root10)  # العودة إلى صفحة الحجز
    )
    back_button.place(relx=0.5, rely=0.85, anchor="center")


def show_tests(options_frame):
    # قائمة الفحوصات وكيفية تجهيزها
    tests = [
        "1. Complete Blood Test: Fast for 8-12 hours.",
        "2. Blood Sugar Test: Fast for 8-12 hours.",
        "3. X-ray: No special preparation required.",
        "4. Urine Test: No special preparation required.",
        "5. Cholesterol Test: Fast for 8-12 hours.",
        "6. Blood Pressure Test: No special preparation required.",
        "7. Liver Function Test: Fast for 8-12 hours."
    ]

    # إخفاء جميع العناصر الحالية في options_frame
    for widget in options_frame.winfo_children():
        widget.place_forget()

    # إضافة إطار لتنسيق الفحوصات بشكل أفضل
    tests_frame = ctk.CTkFrame(
        options_frame,
        width=700,  # تحديد عرض مناسب
        height=400,  # تحديد ارتفاع مناسب
        fg_color="#3e3e52",  # خلفية داكنة للإطار
        corner_radius=10
    )
    tests_frame.place(relx=0.5, rely=0.4, anchor="center")  # وضع الإطار في المنتصف

    # إضافة عنوان الفحوصات
    title_label = ctk.CTkLabel(
        tests_frame,
        text="Tests and Preparation",
        font=("Arial", 20, "bold"),
        text_color="#ffffff"
    )
    title_label.place(relx=0.5, rely=0.1, anchor="center")  # وضع العنوان في الأعلى

    # تنسيق النص بشكل أفضل داخل نفس الإطار لعرض الفحوصات
    test_text = "\n\n".join(tests)  # فصل كل فحص بمسافة إضافية بينهما

    # إضافة النص داخل نافذة الفحوصات مع تعديل التنسيق
    text_label = ctk.CTkLabel(
        tests_frame,
        text=test_text,
        font=("Arial", 14),
        text_color="#ffffff",
        justify="left",
        anchor="nw",  # التوجيه إلى اليسار العلوي
        width=650,  # تحديد عرض مناسب للنص
        height=250,  # تحديد ارتفاع مناسب
    )
    text_label.place(relx=0.5, rely=0.5, anchor="center")  # وضع النص في المنتصف

    # إضافة زر للرجوع إلى الخيارات السابقة
    back_button = ctk.CTkButton(
        options_frame,
        text="Back to Options",
        width=200,
        height=40,
        fg_color="#4e9eff",
        text_color="#ffffff",
        corner_radius=10,
        hover_color="#5ab3ff",
        command=lambda: show_options_page(root)  # الرجوع إلى الخيارات الرئيسية
    )
    back_button.place(relx=0.5, rely=0.85, anchor="center")  # وضع الزر أسفل الإطار مباشرة

    conn = sqlite3.connect('users.db')
    c = conn.cursor()


def create_chat_interface(root121):

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client.connect(("localhost", 9999))

    root121.title("Chat")
    root121.geometry("880x550")
    root121.configure(bg="#1E2A47")

    # عرض الرسائل
    message_display = ctk.CTkTextbox(
        root121,  # استخدام root121 هنا
        width=860,
        height=350,
        corner_radius=5,
        bg_color="#2E3B56",
        text_color="white"
    )
    message_display.place(relx=0.5, rely=0.38, anchor="center")

    # إطار الإدخال
    input_frame = ctk.CTkFrame(root121, width=860, height=50, fg_color="#1E2A47")  # استخدام root121 هنا
    input_frame.place(relx=0.5, rely=0.80, anchor="center")

    # حقل إدخال النص
    message_entry = ctk.CTkEntry(
        input_frame,
        width=700,
        height=40,
        corner_radius=10,
        placeholder_text="Type your message...",
        placeholder_text_color="gray"
    )
    message_entry.pack(side="left", padx=10)

    # زر الإرسال
    send_button = ctk.CTkButton(
        input_frame,
        text="Send",
        width=120,
        height=40,
        fg_color="#4A90E2",
        text_color="white",
        corner_radius=10,
        command= client.send(input("Message: ").encode('utf-8'))
    )
    send_button.pack(side="left")

    # زر العودة للخلف
    back_button = ctk.CTkButton(
        root121,
        text="Back to Options",
        width=200,
        height=40,
        fg_color="#FF6347",  # لون الزر
        text_color="white",
        corner_radius=10,
        hover_color="#FF7F7F",
    )
    back_button.place(relx=0.5, rely=0.9, anchor="center")  # تحديد مكان زر العودة

    return message_display, message_entry, send_button


if __name__ == "__main__":
    create_database()  # إنشاء جداول المستخدمين والمواعيد
    create_doctor_table()  # إنشاء جدول الأطباء مع الحسابات الافتراضية
    root = ctk.CTk()  # إنشاء نافذة التطبيق
    root121 = ctk.CTk()  # تعريف نافذة جديدة
    root.geometry("880x550")
    root.title("Care App")
    show_welcome_page(root)  # عرض صفحة الترحيب
    create_chat_interface(root121)  # تمرير نافذة root الحالية إلى الدالة
    root.mainloop()

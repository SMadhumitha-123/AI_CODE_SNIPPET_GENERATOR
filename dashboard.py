import os
import requests
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from dotenv import load_dotenv
from datetime import datetime

# ---------------- Load API Key ----------------
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("OpenRouter API key not found. Please set OPENROUTER_API_KEY in your .env file.")

API_URL = "https://openrouter.ai/api/v1/chat/completions"
USERS_FILE = "users.txt"

# ---------------- Generate Code Snippet ----------------
def generate_code_snippet(request: str, language: str) -> str:
    full_request = f"Generate a {language} code snippet with explanation for the following request:\n\n{request}"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "openrouter/auto",
        "messages": [{"role": "user", "content": full_request}],
    }
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content'].strip()
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

# ---------------- User Authentication ----------------
def load_users():
    users = {}
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            for line in f:
                if ":" in line:
                    u, p = line.strip().split(":", 1)
                    users[u] = p
    return users

def save_user(username, password):
    with open(USERS_FILE, "a") as f:
        f.write(f"{username}:{password}\n")

# ---------------- Login/Signup GUI ----------------
class LoginSignupGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Login / Signup")
        self.root.geometry("450x320")
        self.root.configure(bg="#000000")

        main_frame = tk.Frame(root, bg="#000000", bd=2, relief="groove")
        main_frame.place(relx=0.5, rely=0.5, anchor="center")

        title = tk.Label(main_frame, text="AI Code Generator Login", font=("Helvetica", 16, "bold"),
                         bg="#000000", fg="#ffffff")
        title.pack(pady=10)

        tk.Label(main_frame, text="Username:", font=("Helvetica", 12), bg="#000000", fg="#ffffff").pack(pady=5)
        self.username_entry = tk.Entry(main_frame, font=("Helvetica", 12), bd=2, relief="groove",
                                       bg="#222222", fg="#ffffff", insertbackground="white")
        self.username_entry.pack(pady=5, ipady=3)

        tk.Label(main_frame, text="Password:", font=("Helvetica", 12), bg="#000000", fg="#ffffff").pack(pady=5)
        self.password_entry = tk.Entry(main_frame, show="*", font=("Helvetica", 12), bd=2, relief="groove",
                                       bg="#222222", fg="#ffffff", insertbackground="white")
        self.password_entry.pack(pady=5, ipady=3)

        btn_frame = tk.Frame(main_frame, bg="#000000")
        btn_frame.pack(pady=15)

        self.login_btn = tk.Button(btn_frame, text="Login", bg="#27ae60", fg="white",
                                   font=("Helvetica", 12, "bold"), width=12,
                                   activebackground="#2ecc71", activeforeground="white", command=self.login)
        self.login_btn.pack(side="left", padx=10)

        self.signup_btn = tk.Button(btn_frame, text="Signup", bg="#2980b9", fg="white",
                                    font=("Helvetica", 12, "bold"), width=12,
                                    activebackground="#3498db", activeforeground="white", command=self.signup)
        self.signup_btn.pack(side="left", padx=10)

        self.users = load_users()

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if username in self.users and self.users[username] == password:
            messagebox.showinfo("Login Successful", f"Welcome, {username}!")
            self.root.destroy()
            main_root = tk.Tk()
            app = CodeSnippetGUI(main_root)
            main_root.mainloop()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def signup(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            messagebox.showerror("Signup Failed", "Username and password cannot be empty.")
            return
        if username in self.users:
            messagebox.showerror("Signup Failed", "Username already exists.")
            return
        save_user(username, password)
        self.users[username] = password
        messagebox.showinfo("Signup Successful", "You can now login with your credentials.")

# ---------------- Code Snippet Generator GUI ----------------
class CodeSnippetGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Code Snippet Generator")
        self.root.geometry("1100x750")
        self.theme = "dark"
        self.root.configure(bg="#000000")

        # ---------------- Left Frame ----------------
        self.left_frame = tk.Frame(root, width=250, bg="#111111")
        self.left_frame.pack(side="left", fill="y")
        tk.Label(self.left_frame, text="Conversation History", bg="#111111",
                 font=("Helvetica", 12, "bold"), fg="#ffffff").pack(pady=10)

        self.search_var = tk.StringVar()
        search_entry = tk.Entry(self.left_frame, textvariable=self.search_var, font=("Helvetica", 11))
        search_entry.pack(padx=10, pady=5, fill="x")
        search_entry.bind("<KeyRelease>", self.search_history)

        self.history_listbox = tk.Listbox(self.left_frame, bg="#000000", fg="#ffffff", font=("Helvetica", 11))
        self.history_listbox.pack(padx=10, pady=5, fill="both", expand=True)
        self.history_listbox.bind("<<ListboxSelect>>", self.load_history_item)

        # ---------------- Right Frame ----------------
        self.right_frame = tk.Frame(root, bg="#000000")
        self.right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Language Selection
        tk.Label(self.right_frame, text="Select Language:", font=("Helvetica", 12),
                 bg="#000000", fg="#ffffff").pack(anchor="w")
        self.language_var = tk.StringVar(value="Python")
        self.language_dropdown = ttk.Combobox(self.right_frame, textvariable=self.language_var,
                                              state="readonly", font=("Helvetica", 12))
        self.language_dropdown['values'] = ["Python", "Java", "C++", "C", "JavaScript", "C#", "Go", "Ruby", "PHP", "Kotlin", "Swift"]
        self.language_dropdown.pack(anchor="w", pady=5)

        # Prompt Input Box
        prompt_frame = tk.LabelFrame(self.right_frame, text="Enter Your Request", bg="#000000", fg="#ffffff",
                                     font=("Helvetica", 12, "bold"))
        prompt_frame.pack(fill="x", pady=5)
        self.text_input = scrolledtext.ScrolledText(prompt_frame, height=5, font=("Consolas", 11),
                                                    bg="#111111", fg="#ffffff", insertbackground="white")
        self.text_input.pack(fill="x", padx=5, pady=5)

        # Buttons
        self.buttons_frame = tk.Frame(self.right_frame, bg="#000000")
        self.buttons_frame.pack(fill="x", pady=5)

        self.generate_btn = tk.Button(self.buttons_frame, text="Generate Snippet", bg="#27ae60", fg="white",
                                      font=("Helvetica", 11, "bold"), command=self.on_generate)
        self.generate_btn.pack(side="left", padx=5)

        self.copy_code_btn = tk.Button(self.buttons_frame, text="Copy Code", bg="#16a085", fg="white",
                                       font=("Helvetica", 11, "bold"), command=self.copy_code)
        self.copy_code_btn.pack(side="left", padx=5)

        self.copy_expl_btn = tk.Button(self.buttons_frame, text="Copy Explanation", bg="#16a085", fg="white",
                                       font=("Helvetica", 11, "bold"), command=self.copy_explanation)
        self.copy_expl_btn.pack(side="left", padx=5)

        self.save_code_btn = tk.Button(self.buttons_frame, text="Save Code", bg="#f39c12", fg="white",
                                       font=("Helvetica", 11, "bold"), command=self.save_code)
        self.save_code_btn.pack(side="left", padx=5)

        self.save_conv_btn = tk.Button(self.buttons_frame, text="Save Conversation", bg="#d35400", fg="white",
                                       font=("Helvetica", 11, "bold"), command=self.save_conversation)
        self.save_conv_btn.pack(side="left", padx=5)

        self.theme_btn = tk.Button(self.buttons_frame, text="Toggle Theme", bg="#8e44ad", fg="white",
                                   font=("Helvetica", 11, "bold"), command=self.toggle_theme)
        self.theme_btn.pack(side="left", padx=5)

        self.new_chat_btn = tk.Button(self.buttons_frame, text="New Chat", bg="#2980b9", fg="white",
                                      font=("Helvetica", 11, "bold"), command=self.new_chat)
        self.new_chat_btn.pack(side="left", padx=5)

        self.clear_history_btn = tk.Button(self.buttons_frame, text="Clear History", bg="#c0392b", fg="white",
                                           font=("Helvetica", 11, "bold"), command=self.clear_history)
        self.clear_history_btn.pack(side="left", padx=5)

        # Code Output Box
        code_frame = tk.LabelFrame(self.right_frame, text="Generated Code", bg="#000000", fg="#ffffff",
                                   font=("Helvetica", 12, "bold"))
        code_frame.pack(fill="both", expand=True, pady=5)
        self.code_output = scrolledtext.ScrolledText(code_frame, height=15, font=("Consolas", 11),
                                                     bg="#111111", fg="#ffffff", insertbackground="white")
        self.code_output.pack(fill="both", expand=True, padx=5, pady=5)

        # Explanation Box
        explanation_frame = tk.LabelFrame(self.right_frame, text="Explanation", bg="#000000", fg="#ffffff",
                                         font=("Helvetica", 12, "bold"))
        explanation_frame.pack(fill="both", expand=True, pady=5)
        self.explanation_output = scrolledtext.ScrolledText(explanation_frame, height=15, font=("Consolas", 11),
                                                            bg="#111111", fg="#ffffff", insertbackground="white")
        self.explanation_output.pack(fill="both", expand=True, padx=5, pady=5)

        # Conversation Display
        tk.Label(self.right_frame, text="Conversation:", font=("Helvetica", 12),
                 bg="#000000", fg="#ffffff").pack(anchor="w", pady=5)
        self.conversation_display = scrolledtext.ScrolledText(self.right_frame, height=8, font=("Consolas", 11),
                                                              bg="#111111", fg="#ffffff", state="disabled",
                                                              insertbackground="white")
        self.conversation_display.pack(fill="both", expand=False, pady=5)

        self.history = []

    # ---------------- Generate Code ----------------
    def on_generate(self):
        request = self.text_input.get("1.0", "end-1c").strip()
        language = self.language_var.get()
        if not request:
            messagebox.showerror("Input Error", "Please enter a request.")
            return

        self.code_output.delete("1.0", "end")
        self.explanation_output.delete("1.0", "end")
        self.code_output.insert("1.0", "Generating code...\n")
        self.root.update()

        snippet = generate_code_snippet(request, language)

        # Split code & explanation
        if "# Explanation" in snippet:
            code_part, explanation_part = snippet.split("# Explanation", 1)
        elif "Explanation:" in snippet:
            code_part, explanation_part = snippet.split("Explanation:", 1)
        else:
            code_part = snippet
            explanation_part = ""

        self.code_output.delete("1.0", "end")
        self.code_output.insert("1.0", code_part.strip())
        self.explanation_output.delete("1.0", "end")
        self.explanation_output.insert("1.0", explanation_part.strip())

        # Update conversation display
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.append_conversation(f"[{timestamp}] You ({language}): {request}\n")
        self.append_conversation(f"[{timestamp}] AI Response:\n{snippet}\n\n")

        # Update history
        self.history.append((language, request, code_part, explanation_part))
        self.update_history()

    # ---------------- Clipboard Functions ----------------
    def copy_code(self):
        code = self.code_output.get("1.0", "end-1c")
        if code.strip():
            self.root.clipboard_clear()
            self.root.clipboard_append(code)
            messagebox.showinfo("Copied", "Code copied to clipboard!")

    def copy_explanation(self):
        explanation = self.explanation_output.get("1.0", "end-1c")
        if explanation.strip():
            self.root.clipboard_clear()
            self.root.clipboard_append(explanation)
            messagebox.showinfo("Copied", "Explanation copied to clipboard!")

    # ---------------- Save Functions ----------------
    def save_code(self):
        code = self.code_output.get("1.0", "end-1c")
        if not code.strip():
            messagebox.showerror("Error", "No code to save!")
            return
        ext = self.language_var.get().lower()
        filename = f"code_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
        with open(filename, "w") as f:
            f.write(code)
        messagebox.showinfo("Saved", f"Code saved as {filename}")

    def save_conversation(self):
        conversation = self.conversation_display.get("1.0", "end-1c")
        if not conversation.strip():
            messagebox.showerror("Error", "No conversation to save!")
            return
        filename = f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, "w") as f:
            f.write(conversation)
        messagebox.showinfo("Saved", f"Conversation saved as {filename}")

    # ---------------- Append Conversation ----------------
    def append_conversation(self, message):
        self.conversation_display.configure(state="normal")
        self.conversation_display.insert("end", message)
        self.conversation_display.see("end")
        self.conversation_display.configure(state="disabled")

    # ---------------- Theme Toggle ----------------
    def toggle_theme(self):
        if self.theme == "dark":
            self.theme = "light"
            bg_color = "#f0f0f0"
            fg_color = "#000000"
            input_bg = "#ffffff"
        else:
            self.theme = "dark"
            bg_color = "#000000"
            fg_color = "#ffffff"
            input_bg = "#111111"

        self.root.configure(bg=bg_color)
        self.left_frame.configure(bg=bg_color)
        self.right_frame.configure(bg=bg_color)
        self.text_input.configure(bg=input_bg, fg=fg_color, insertbackground=fg_color)
        self.code_output.configure(bg=input_bg, fg=fg_color, insertbackground=fg_color)
        self.explanation_output.configure(bg=input_bg, fg=fg_color, insertbackground=fg_color)
        self.conversation_display.configure(bg=input_bg, fg=fg_color, insertbackground=fg_color)
        self.history_listbox.configure(bg=bg_color, fg=fg_color)
        for widget in self.right_frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.configure(bg=bg_color, fg=fg_color)

    # ---------------- History ----------------
    def update_history(self):
        self.history_listbox.delete(0, "end")
        for lang, req, _, _ in self.history[-50:]:
            self.history_listbox.insert("end", f"{lang}: {req}")

    def load_history_item(self, event):
        selection = self.history_listbox.curselection()
        if selection:
            index = selection[0]
            lang, req, code, explanation = self.history[-50:][index]
            self.language_var.set(lang)
            self.text_input.delete("1.0", "end")
            self.text_input.insert("1.0", req)
            self.code_output.delete("1.0", "end")
            self.code_output.insert("1.0", code)
            self.explanation_output.delete("1.0", "end")
            self.explanation_output.insert("1.0", explanation)

    def search_history(self, event):
        query = self.search_var.get().lower()
        self.history_listbox.delete(0, "end")
        for lang, req, _, _ in self.history[-50:]:
            if query in req.lower() or query in lang.lower():
                self.history_listbox.insert("end", f"{lang}: {req}")

    def new_chat(self):
        self.text_input.delete("1.0", "end")
        self.code_output.delete("1.0", "end")
        self.explanation_output.delete("1.0", "end")
        self.conversation_display.configure(state="normal")
        self.conversation_display.delete("1.0", "end")
        self.conversation_display.configure(state="disabled")
        self.language_var.set("Python")

    def clear_history(self):
        if messagebox.askyesno("Clear History", "Are you sure you want to clear all conversation history?"):
            self.history = []
            self.history_listbox.delete(0, "end")
            self.conversation_display.configure(state="normal")
            self.conversation_display.delete("1.0", "end")
            self.conversation_display.configure(state="disabled")


# ---------------- Run Login/Signup ----------------
if __name__ == "__main__":
    root = tk.Tk()
    app = LoginSignupGUI(root)
    root.mainloop()

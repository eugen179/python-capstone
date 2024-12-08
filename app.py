import customtkinter as ctk
from tkinter import messagebox
import sqlite3
import praw
import time
import webbrowser  
app = ctk.CTk()
app.geometry('600x600')
app.title('Reddit Topic Notification Bot')

client_id = 'ApCdeQC-OzxkvTp2Djb_PQ'
client_secret = 'wll_PHgJ5_JukS4KDqA1k8hEr5aQnQ'
user_agent = 'Brilliant-Store60'
reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     user_agent=user_agent)

def setup_database():
    conn = sqlite3.connect("preferences.db")
    cursor = conn.cursor()
    cursor.execute
    conn.commit()
    conn.close()

def save_inputs():
    subreddit = subreddit_entry.get()
    keywords = keywords_entry.get()
    
    if not subreddit.strip():
        messagebox.showerror("Input Error", "Subreddit field cannot be empty.")
        return
    if not keywords.strip():
        messagebox.showerror("Input Error", "Keywords field cannot be empty.")
        return

    try:
        conn = sqlite3.connect("preferences.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO preferences (subreddit, keywords) VALUES (?, ?)", (subreddit, keywords))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Preferences saved successfully!")
        display_preferences()  
    except Exception as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")

def display_preferences():
    for widget in preferences_frame.winfo_children():
        widget.destroy()

    try:
        conn = sqlite3.connect("preferences.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, subreddit, keywords FROM preferences")
        rows = cursor.fetchall()
        conn.close()

        if rows:
            for i, (id, subreddit, keywords) in enumerate(rows, start=1):
                entry_label = ctk.CTkLabel(preferences_frame, text=f"{i}. Subreddit: {subreddit} | Keywords: {keywords}", anchor="w")
                entry_label.pack(pady=2, fill="x")
                delete_button = ctk.CTkButton(preferences_frame, text="Delete", width=400, command=lambda id=id: delete_preference(id))
                delete_button.pack(pady=2, fill="x")
        else:
            empty_label = ctk.CTkLabel(preferences_frame, text="No preferences saved yet.", anchor="center")
            empty_label.pack(pady=10)
    except Exception as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")

def delete_preference(id):
    try:
        conn = sqlite3.connect("preferences.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM preferences WHERE id=?", (id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Deleted", "Preference deleted successfully!")
        display_preferences()  
    except Exception as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")

def fetch_posts():
    try:
        conn = sqlite3.connect("preferences.db")
        cursor = conn.cursor()
        cursor.execute("SELECT subreddit, keywords FROM preferences")
        rows = cursor.fetchall()
        conn.close()

        if rows:
            for subreddit, keywords in rows:
                print(f"Fetching posts from subreddit: {subreddit} for keywords: {keywords}")
                posts = reddit.subreddit(subreddit).search(keywords, sort='new', time_filter='day', limit=100)
                posts_list = list(posts)
                print(f"Found {len(posts_list)} posts for subreddit: {subreddit} with keywords: {keywords}")
                
                if len(posts_list) == 0:
                    print(f"No posts found for subreddit: {subreddit} and keywords: {keywords}")
                
                display_posts(posts_list, subreddit, keywords)
        else:
            messagebox.showinfo("No Preferences", "No preferences found in the database.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while fetching posts: {e}")

def display_posts(posts, subreddit, keywords):
    if posts:
        for post in posts:
            post_title = post.title
            post_url = post.url
            post_text = f"Title: {post_title}\nURL: {post_url}"

            post_label = ctk.CTkLabel(posts_frame, text=post_text, anchor="w")
            post_label.pack(pady=5, fill="x")
            link_button = ctk.CTkButton(posts_frame, text="Open in Reddit", width=400, command=lambda subreddit=subreddit, keywords=keywords: open_reddit(subreddit, keywords))
            link_button.pack(pady=5, fill="x")
    else:
        messagebox.showinfo("No Posts", "No posts were found matching the keywords.")

def open_reddit(subreddit, keywords):
    search_query = "+".join(keywords.split(","))
    reddit_url = f"https://www.reddit.com/r/{subreddit}/search/?q={search_query}&restrict_sr=on"
    webbrowser.open(reddit_url) 
def toggle_mode():
    if ctk.get_appearance_mode() == "Light":
        ctk.set_appearance_mode("Dark")
    else:
        ctk.set_appearance_mode("Light")

title_label = ctk.CTkLabel(app, text="Reddit Topic Notification Bot", font=("Arial", 20))
title_label.pack(pady=10)

mode_toggle = ctk.CTkButton(app, text="Toggle Dark/Light Mode", command=toggle_mode)
mode_toggle.pack(pady=5)

subreddit_label = ctk.CTkLabel(app, text="Enter Subreddit:")
subreddit_label.pack(pady=5)
subreddit_entry = ctk.CTkEntry(app, width=400, placeholder_text="Enter Subreddit")
subreddit_entry.pack(pady=5)

keywords_label = ctk.CTkLabel(app, text="Enter Keywords (comma-separated):")
keywords_label.pack(pady=5)
keywords_entry = ctk.CTkEntry(app, width=400, placeholder_text="Enter Keywords")
keywords_entry.pack(pady=5)

save_button = ctk.CTkButton(app, text="Save Inputs", width=400, command=save_inputs)
save_button.pack(pady=20)

preferences_label = ctk.CTkLabel(app, text="Saved Preferences:", font=("Arial", 16))
preferences_label.pack(pady=10)
preferences_frame = ctk.CTkFrame(app, width=500, height=300)
preferences_frame.pack(pady=10, padx=20, fill="both", expand=True)

fetch_button = ctk.CTkButton(app, text="Fetch Posts", width=400, command=fetch_posts)
fetch_button.pack(pady=20)

posts_label = ctk.CTkLabel(app, text="Fetched Posts:", font=("Arial", 16))
posts_label.pack(pady=10)
posts_frame = ctk.CTkFrame(app, width=500, height=300)
posts_frame.pack(pady=10, padx=20, fill="both", expand=True)

setup_database()
display_preferences()
app.mainloop()

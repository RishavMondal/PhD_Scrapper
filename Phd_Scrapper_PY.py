import requests
from bs4 import BeautifulSoup
import pandas as pd
import urllib.parse
import re
import os
import time
import tkinter as tk
from tkinter import ttk, messagebox

def get_program_details(university_url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    
    try:
        response = requests.get(university_url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None, None, None
        
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text()
        
        deadline_pattern = re.compile(r"Deadline[:\s]*([A-Za-z]+\s\d{1,2},\s\d{4})", re.IGNORECASE)
        deadlines = deadline_pattern.findall(text)
        deadline = deadlines[0] if deadlines else "No deadline found"
        
        desc_pattern = re.compile(r"(PhD in .*?)\.\s", re.IGNORECASE)
        desc_match = desc_pattern.search(text)
        description = desc_match.group(1) if desc_match else "No description found"
        
        advisor_pattern = re.compile(r"Advisor[:\s]*(Dr\.?\s[A-Za-z]+\s[A-Za-z]+)", re.IGNORECASE)
        advisors = advisor_pattern.findall(text)
        advisor = advisors[0] if advisors else "No advisor found"
        
        return deadline, description, advisor
    except requests.RequestException:
        return None, None, None

def search_phd_programs(state, department, course, gre_requirement):
    base_url = "https://www.google.com/search?q="
    query = "PhD programs with open applications in " + (state if state else "USA")
    if department:
        query += " in " + department
    if course:
        query += " " + course
    if gre_requirement:
        query += " GRE " + gre_requirement
    query = urllib.parse.quote(query)
    search_url = base_url + query
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    
    response = requests.get(search_url, headers=headers)
    if response.status_code != 200:
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    search_results = []
    
    for g in soup.find_all('div', class_='tF2Cxc'):
        try:
            title = g.find('h3').text
            link = g.find('a')['href']
            deadline, description, advisor = get_program_details(link)
            
            if deadline:
                search_results.append((title, description, link, deadline, advisor))
        except AttributeError:
            continue
    
    return search_results

def search():
    state = state_var.get()
    department = department_var.get()
    course = course_var.get()
    gre_requirement = gre_var.get()
    
    results = search_phd_programs(state, department, course, gre_requirement)
    
    if results:
        df = pd.DataFrame(results, columns=["PhD Program", "Description", "Link", "Deadline", "Advisor"])
        df.to_csv("phd_programs_filtered.csv", index=False)
        messagebox.showinfo("Success", "Results saved to phd_programs_filtered.csv")
    else:
        messagebox.showinfo("No Results", "No PhD programs found with the given criteria.")

# GUI Setup
root = tk.Tk()
root.title("PhD Program Search Tool")
root.geometry("500x400")

tk.Label(root, text="State:").pack()
state_var = tk.Entry(root)
state_var.pack()

tk.Label(root, text="Department:").pack()
department_var = tk.Entry(root)
department_var.pack()

tk.Label(root, text="Course:").pack()
course_var = tk.Entry(root)
course_var.pack()

tk.Label(root, text="GRE Requirement (Required/Not Required):").pack()
gre_var = tk.Entry(root)
gre_var.pack()

tk.Button(root, text="Search", command=search).pack()
root.mainloop()

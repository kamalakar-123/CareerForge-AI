# 🚀 Quick Start Guide - AI Interview Platform

## Get Started in 3 Minutes!

### Step 1: Install Dependencies (1 minute)

Open your terminal/command prompt in the project folder and run:

```bash
pip install flask python-dotenv google-generativeai werkzeug
```

Or simply:

```bash
pip install -r requirements.txt
```

### Step 2: Configure Gemini API Key (1 minute)

1. Get your FREE Gemini API key:
   - Visit: https://makersuite.google.com/app/apikey
   - Sign in with your Google account
   - Click "Create API Key"
   - Copy the key

2. Open the `.env` file in the project folder

3. Replace `your_gemini_api_key_here` with your actual API key:
   ```
   GEMINI_API_KEY=AIzaSyA...your_actual_key_here
   ```

4. (Optional) Change the SECRET_KEY for security:
   ```
   SECRET_KEY=my-unique-secret-key-12345
   ```

### Step 3: Run the Application (30 seconds)

```bash
python app.py
```

You should see:
```
✓ Database initialized
✓ Flask application starting...
✓ Access the platform at: http://127.0.0.1:5000
```

### Step 4: Start Using! (30 seconds)

1. Open your browser
2. Go to: http://127.0.0.1:5000
3. Click "Get Started" or "Register"
4. Create your account
5. Start your first mock interview!

---

## First Time User Flow

### 1. Register Account
- Username: `john_student`
- Email: `john@example.com`
- Password: `password123`

### 2. Login
- Use your credentials to login

### 3. Start Interview
- Click "Start Mock Interview" from dashboard
- Select Role: `Python Developer`
- Select Difficulty: `Easy`
- Click "Start Interview 🚀"

### 4. Answer Questions
- Type your answer in the text box
- Or click 🎤 to use voice input
- Click "Send Answer"
- AI will ask follow-up questions

### 5. End Interview
- Click "End Interview" button
- View your scores and feedback

---

## Testing Without API Key

If you don't have a Gemini API key yet, the platform will still work but with limited AI features:
- ✅ Authentication works
- ✅ Dashboard works
- ✅ Assignments work
- ✅ Database works
- ⚠️ AI interviewer will show error messages
- ⚠️ AI evaluation won't work

To test basic features without API:
1. Skip Step 2 (API configuration)
2. Run the app anyway
3. Explore dashboard, assignments, and progress pages

---

## Troubleshooting

### "Module not found" error
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### "Port already in use" error
The default port (5000) is busy. Change it in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Use port 5001
```

### Database error
Delete `database.db` file and restart:
```bash
# Windows
del database.db
python app.py

# Mac/Linux
rm database.db
python app.py
```

### Voice input not working
- Use Chrome, Edge, or Safari browser
- Allow microphone permissions when prompted
- Voice input requires localhost or HTTPS

---

## Common Questions

**Q: Is the Gemini API free?**
A: Yes! Google provides a generous free tier for Gemini API.

**Q: Do I need an internet connection?**
A: Yes, for AI features. Database and UI work offline.

**Q: Can I add my own questions?**
A: Yes! Edit the database or modify `insert_sample_questions()` in app.py

**Q: How many users can register?**
A: Unlimited! SQLite can handle thousands of users for learning purposes.

**Q: Can I deploy this to production?**
A: Yes! See README.md for production deployment checklist.

---

## Sample Test Account

For testing, you can create:
- Username: `test_student`
- Email: `test@example.com`
- Password: `test123`

Then:
1. Upload a resume (any PDF)
2. Try different roles
3. Test voice input
4. Complete multiple interviews
5. Check progress analytics

---

## Features to Try

✅ **Authentication**
   - Register → Login → Logout

✅ **Mock Interview**
   - Setup → Chat → End → Results

✅ **Voice Input**
   - Click 🎤 during interview

✅ **Assignments**
   - View coding problems
   - Show hints

✅ **Progress**
   - Complete 3+ interviews
   - See the chart

✅ **Resume Upload**
   - Upload PDF/DOCX
   - Check dashboard

---

## Next Steps

After getting started:

1. **Complete 3 interviews** to see progress chart
2. **Try different roles** (Python, Full Stack, Data Science)
3. **Test all difficulty levels** (Easy, Medium, Hard)
4. **Practice assignments** from assignments page
5. **Use voice input** for realistic practice

---

## Need Help?

1. Check **README.md** for detailed documentation
2. Review **app.py** for code comments
3. Check console logs for errors
4. Verify `.env` configuration

---

## Project Structure at a Glance

```
ai_inetrview/
├── app.py                    # ⚙️ Main application
├── .env                      # 🔑 Your API key goes here
├── requirements.txt          # 📦 Dependencies
├── README.md                 # 📖 Full documentation
├── templates/               # 🎨 HTML pages (10 files)
├── static/
│   ├── css/style.css       # 💅 Styling
│   └── js/script.js        # ⚡ Interactivity
└── uploads/                # 📄 Resume storage
```

---

## Success Checklist

- [ ] Dependencies installed
- [ ] Gemini API key configured in .env
- [ ] App runs without errors
- [ ] Can access http://127.0.0.1:5000
- [ ] Can register and login
- [ ] Can start an interview
- [ ] AI responds to messages
- [ ] Can end interview and see results
- [ ] Progress chart displays data

---

**You're all set! Start preparing for your dream job! 🎯🚀**

Having issues? Check README.md for detailed troubleshooting.

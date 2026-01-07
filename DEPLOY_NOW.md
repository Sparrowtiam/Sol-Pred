# ⚡ Quick Reference - Deploy in 3 Commands

## Step 1️⃣: Create GitHub Repo
Go to https://github.com/new
- **Name**: `sol-usd-prediction`
- **Visibility**: Public
- Click "Create Repository"
- Copy the HTTPS URL

## Step 2️⃣: Push to GitHub
```powershell
cd "c:\Users\HP\Prediction"
git remote add origin https://github.com/Sparrowtiam/sol-usd-prediction.git
git branch -M main
git push -u origin main
```

## Step 3️⃣: Deploy to Streamlit
1. Go to https://streamlit.io/cloud
2. Click "New app"
3. Select: `Sparrowtiam/sol-usd-prediction` → `main` → `streamlit_app.py`
4. Click "Deploy!"

---

## ✅ What You Get

- **Live URL**: `https://share.streamlit.io/sparrowtiam/sol-usd-prediction/main/streamlit_app.py`
- **Features**: 
  - 📈 30-day price forecasts
  - 📊 15+ technical indicators
  - 🎯 Real-time trading signals (85% confidence)
  - 📉 12-month backtest results
- **Updates**: Auto-sync when you push to GitHub

---

## 🧪 Test Locally First (Optional)
```powershell
cd "c:\Users\HP\Prediction"
pip install streamlit
streamlit run streamlit_app.py
```
Open: `http://localhost:8501`

---

## 📂 What's Ready to Deploy

✅ 7 Python modules (1,800+ lines)
✅ Streamlit web app
✅ 7 documentation files
✅ Git repository initialized
✅ All dependencies in requirements.txt
✅ .gitignore configured

---

**Time to deploy**: ~15 minutes | **Cost**: FREE (Streamlit Cloud)

---

For detailed instructions, see: **GITHUB_DEPLOYMENT.md**

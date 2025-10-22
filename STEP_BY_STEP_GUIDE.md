# 🚀 Step-by-Step Calendar Assistant Deployment

## Prerequisites ✅
- AWS Account with root access
- Python 3.9+
- AWS CLI configured

## Step 1: Enable Bedrock Model Access (REQUIRED FIRST)

**⚠️ IMPORTANT: Do this BEFORE deploying the agent**

1. Go to: https://console.aws.amazon.com/bedrock/
2. Click **"Model access"** (left menu)
3. Click **"Request model access"**
4. Check **"Claude 3 Sonnet"** or **"Claude 3.5 Sonnet"**
5. Submit request (requires valid payment method)
6. Wait for approval (usually instant)

## Step 2: Deploy Calendar Assistant

Run the deployment script:
```bash
python3 deploy_step_by_step.py
```

## Step 3: Test Your Assistant

**AWS Console:**
1. Go to: https://console.aws.amazon.com/bedrock/
2. Navigate: **Agents** → **bhagyesh-calendar-assistant**
3. Click **Test**
4. Try: **"Hello bhagyesh!"**

**Command Line:**
```bash
python3 test_bhagyesh_final.py
```

## Expected Results

✅ Agent responds with personalized messages for bhagyesh
✅ Calendar operations work (list, add, delete)
✅ No access denied errors

---

**Follow these steps in order for guaranteed success!** 🎉
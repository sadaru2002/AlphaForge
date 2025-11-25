# AlphaForge Oracle VM Deployment
# IP: 161.118.218.33

$ErrorActionPreference = "Stop"

$IpAddress = "161.118.218.33"
$User = "ubuntu"
$RemoteHost = "$User@$IpAddress"
$RemoteDir = "/opt/alphaforge"

# SSH Key
$TempKeyPath = "$env:TEMP\oracle_key.pem"
@'
-----BEGIN RSA PRIVATE KEY-----
MIIEogIBAAKCAQEA7BrG2CyvvW82CZha18shMyOsTKZZzmviwREhuQgSycjFAlCE
Fh/Dkulztp1mV7hUReBMg4OANBM8z+m6ljOHw/lxpnnkRATcyFBPKL42ouDLvjOa
HU9J+vrMpPh57XiPsypm4hb9LwOg4fc2tYIwo/RpUEmNz+cb6naBh3huy+9NnSAI
VEraS2YRGTOL17W2MwlnSD+eBqvsICFKlocWYp+hYM1xQsAEbayotD9kVgOqQp/v
DL322PJytC/l1+/+Bw4v9zTdllK5JKEMLuFkEp7wY2DnixHigokamyxZb2j72tYq
dlICOaCQEeP3XSg4aIGCJFqb9V55soacKpIEnwIDAQABAoIBADM/SKPJZ0fV6MPC
Zw1p0MX52z8z6FBOyIQhhNFVuEZGJsTu1wy6TkgIFg6wMXOe1ePo4JK3K0+iUVPL
pq1NeA2IiiuZT3uYFpgAHn54cwF9i5u4NZ5hBGzOnTa9nDF4NrCr5nLyjHf08Km7
cAuLu6UKuwUrQfW7cyq8GDdgY6Qt3U65HMYCLPsHxwYtl3R2OaAcT1q7mC7re2ro
Y3f3vjEYyLcjUQVA4a0pu7s4fPOgG3LRhk2Skr5KFwuhuWGjASurwsVwhcp8DxnX
JCW/fXaIdS0/W/KQuQlq7IfbWZM4JB5KAYOgJxiJJf58BlPjecW7VlgLPGtva2BQ
N9yEtlECgYEA9/efBRkePDQ6RxUgW3x4C/wWuJD79yNNt21xmHuWDZvWFqmIZ4Bj
H19WQrTEorCXMlekxaxqt5q37yuJYtEDRCDpLnKG54VggOLpniGFk4A1X5EfVTds
y4nllfE26iE0J1j3g8ggrJ1ArJOfv3DGSnAhEOR9o9sbYniYuDJojfkCgYEA88DH
cSItluyYgUHGGTre90BltShouea0D55Dh7L414XkczImK9oxJYTD1kLITNjSE0PP
7o/fxqITeTDZiBh23uM6+MAZQIkX6W8U0FnZqQ0dI83NJhjkbTCbx9lGDR/aP2qr
htC3SYpyF3AMhdBPwlxqzpciu7G9y03N/2H9LVcCgYB9RpcKZlRGKkS/IMdGMS4d
L/Dyshz6ENX0s9BOLzHyEicpL+GAGPb7JJlZ/iXR49GfV3QhgigwNnRy2tYAHIS/
6LimBKpvUY0d0IYio+DuUjmk3Jat4OCQPEzHYiRSSRAmSOZTp8oKKzA/gB2XBIzJ
krjB5g4ruEiviSnu9VipUQKBgGDrA+H93valeDXcuzGI8OKKnmYbfRh9nJahLOSl
yr+XIzCSfg7toKD0WxG0WAQGKfEzA1gtqKJIC0oinDu6znjtDKOfber1F6bfXf1B
3IOVDUMRL0K4nwqzSx15TJsnURXqCe1+y4HYJGkhSjlijHQRXv5ppYvPrlFJzGCA
y7PdAoGATS6yFLwpobWXShSLKOAG86jXukNtAzXSR3NS2D6Kx/xmWVbK9pb4+GuU
Z3SaMx1tSjhoFPJHF1X3OPp2GnyzLwqznJo3GdOvQVBbvZmsVJ/PjOQFMohtOsb7
bsCMnKrJxojKiKS2SYIT+UcBYsJV61i2qOWr51lB51/GR/at+DQ=
-----END RSA PRIVATE KEY-----
'@ | Out-File -FilePath $TempKeyPath -Encoding ASCII

Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "🚀 Deploying to $IpAddress" -ForegroundColor Cyan
Write-Host "================================`n" -ForegroundColor Cyan

# 1. Test Connection
Write-Host "📡 Testing connection..." -ForegroundColor Yellow
ssh -i $TempKeyPath -o StrictHostKeyChecking=no $RemoteHost "echo 'Connected'"

# 2. Clean VM
Write-Host "`n🧹 Cleaning VM..." -ForegroundColor Yellow
ssh -i $TempKeyPath $RemoteHost "sudo rm -rf $RemoteDir/*"

# 3. Install Docker
Write-Host "`n🐳 Installing Docker..." -ForegroundColor Yellow
ssh -i $TempKeyPath $RemoteHost "command -v docker || { curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh && sudo usermod -aG docker ubuntu && rm get-docker.sh; }"

# 4. Create Directory
Write-Host "`n📁 Creating directory..." -ForegroundColor Yellow
ssh -i $TempKeyPath $RemoteHost "sudo mkdir -p $RemoteDir && sudo chown -R ubuntu:ubuntu $RemoteDir"

# 5. Package & Upload
Write-Host "`n📦 Packaging..." -ForegroundColor Yellow
tar --exclude=venv --exclude=__pycache__ --exclude=.git --exclude=trading_signals.db --exclude=backtest_results --exclude=archive -cf deploy.tar .

Write-Host "⬆️  Uploading..." -ForegroundColor Yellow
scp -i $TempKeyPath deploy.tar "$RemoteHost`:$RemoteDir/"
Remove-Item deploy.tar

# 6. Deploy
Write-Host "`n🚀 Deploying..." -ForegroundColor Yellow
ssh -i $TempKeyPath $RemoteHost "cd $RemoteDir && tar -xf deploy.tar && rm deploy.tar && docker compose up -d --build"

Remove-Item $TempKeyPath -Force

Write-Host "`n================================" -ForegroundColor Green
Write-Host "✅ Deployed!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host "URL: http://$IpAddress`:5000/health`n" -ForegroundColor White

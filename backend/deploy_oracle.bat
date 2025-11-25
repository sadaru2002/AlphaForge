@echo off
echo ================================
echo AlphaForge Oracle VM Deployment
echo ================================

set IP=161.118.218.33
set USER=ubuntu
set REMOTE=%USER%@%IP%
set DIR=/opt/alphaforge

REM Create SSH key file
echo -----BEGIN RSA PRIVATE KEY----- > %TEMP%\oracle.key
echo MIIEogIBAAKCAQEA7BrG2CyvvW82CZha18shMyOsTKZZzmviwREhuQgSycjFAlCE >> %TEMP%\oracle.key
echo Fh/Dkulztp1mV7hUReBMg4OANBM8z+m6ljOHw/lxpnnkRATcyFBPKL42ouDLvjOa >> %TEMP%\oracle.key
echo HU9J+vrMpPh57XiPsypm4hb9LwOg4fc2tYIwo/RpUEmNz+cb6naBh3huy+9NnSAI >> %TEMP%\oracle.key
echo VEraS2YRGTOL17W2MwlnSD+eBqvsICFKlocWYp+hYM1xQsAEbayotD9kVgOqQp/v >> %TEMP%\oracle.key
echo DL322PJytC/l1+/+Bw4v9zTdllK5JKEMLuFkEp7wY2DnixHigokamyxZb2j72tYq >> %TEMP%\oracle.key
echo dlICOaCQEeP3XSg4aIGCJFqb9V55soacKpIEnwIDAQABAoIBADM/SKPJZ0fV6MPC >> %TEMP%\oracle.key
echo Zw1p0MX52z8z6FBOyIQhhNFVuEZGJsTu1wy6TkgIFg6wMXOe1ePo4JK3K0+iUVPL >> %TEMP%\oracle.key
echo pq1NeA2IiiuZT3uYFpgAHn54cwF9i5u4NZ5hBGzOnTa9nDF4NrCr5nLyjHf08Km7 >> %TEMP%\oracle.key
echo cAuLu6UKuwUrQfW7cyq8GDdgY6Qt3U65HMYCLPsHxwYtl3R2OaAcT1q7mC7re2ro >> %TEMP%\oracle.key
echo Y3f3vjEYyLcjUQVA4a0pu7s4fPOgG3LRhk2Skr5KFwuhuWGjASurwsVwhcp8DxnX >> %TEMP%\oracle.key
echo JCW/fXaIdS0/W/KQuQlq7IfbWZM4JB5KAYOgJxiJJf58BlPjecW7VlgLPGtva2BQ >> %TEMP%\oracle.key
echo N9yEtlECgYEA9/efBRkePDQ6RxUgW3x4C/wWuJD79yNNt21xmHuWDZvWFqmIZ4Bj >> %TEMP%\oracle.key
echo H19WQrTEorCXMlekxaxqt5q37yuJYtEDRCDpLnKG54VggOLpniGFk4A1X5EfVTds >> %TEMP%\oracle.key
echo y4nllfE26iE0J1j3g8ggrJ1ArJOfv3DGSnAhEOR9o9sbYniYuDJojfkCgYEA88DH >> %TEMP%\oracle.key
echo cSItluyYgUHGGTre90BltShouea0D55Dh7L414XkczImK9oxJYTD1kLITNjSE0PP >> %TEMP%\oracle.key
echo 7o/fxqITeTDZiBh23uM6+MAZQIkX6W8U0FnZqQ0dI83NJhjkbTCbx9lGDR/aP2qr >> %TEMP%\oracle.key
echo htC3SYpyF3AMhdBPwlxqzpciu7G9y03N/2H9LVcCgYB9RpcKZlRGKkS/IMdGMS4d >> %TEMP%\oracle.key
echo L/Dyshz6ENX0s9BOLzHyEicpL+GAGPb7JJlZ/iXR49GfV3QhgigwNnRy2tYAHIS/ >> %TEMP%\oracle.key
echo 6LimBKpvUY0d0IYio+DuUjmk3Jat4OCQPEzHYiRSSRAmSOZTp8oKKzA/gB2XBIzJ >> %TEMP%\oracle.key
echo krjB5g4ruEiviSnu9VipUQKBgGDrA+H93valeDXcuzGI8OKKnmYbfRh9nJahLOSl >> %TEMP%\oracle.key
echo yr+XIzCSfg7toKD0WxG0WAQGKfEzA1gtqKJIC0oinDu6znjtDKOfber1F6bfXf1B >> %TEMP%\oracle.key
echo 3IOVDUMRL0K4nwqzSx15TJsnURXqCe1+y4HYJGkhSjlijHQRXv5ppYvPrlFJzGCA >> %TEMP%\oracle.key
echo y7PdAoGATS6yFLwpobWXShSLKOAG86jXukNtAzXSR3NS2D6Kx/xmWVbK9pb4+GuU >> %TEMP%\oracle.key
echo Z3SaMx1tSjhoFPJHF1X3OPp2GnyzLwqznJo3GdOvQVBbvZmsVJ/PjOQFMohtOsb7 >> %TEMP%\oracle.key
echo bsCMnKrJxojKiKS2SYIT+UcBYsJV61i2qOWr51lB51/GR/at+DQ= >> %TEMP%\oracle.key
echo -----END RSA PRIVATE KEY----- >> %TEMP%\oracle.key

echo.
echo [1/6] Testing connection...
ssh -i %TEMP%\oracle.key -o StrictHostKeyChecking=no %REMOTE% "echo Connected"
if errorlevel 1 goto cleanup

echo.
echo [2/6] Cleaning VM...
ssh -i %TEMP%\oracle.key %REMOTE% "sudo rm -rf %DIR%/* ; sudo mkdir -p %DIR% ; sudo chown -R ubuntu:ubuntu %DIR%"

echo.
echo [3/6] Installing Docker...
ssh -i %TEMP%\oracle.key %REMOTE% "if ! command -v docker ; then curl -fsSL https://get.docker.com -o get-docker.sh ; sudo sh get-docker.sh ; sudo usermod -aG docker ubuntu ; sudo rm get-docker.sh ; fi"

echo.
echo [4/6] Packaging files...
tar --exclude=venv --exclude=__pycache__ --exclude=.git --exclude=trading_signals.db --exclude=backtest_results --exclude=archive -cf deploy.tar .

echo.
echo [5/6] Uploading package...
scp -i %TEMP%\oracle.key deploy.tar %REMOTE%:%DIR%/
del deploy.tar

echo.
echo [6/6] Deploying with Docker...
REM Use sudo docker since the user might not be in the docker group yet
ssh -i %TEMP%\oracle.key %REMOTE% "cd %DIR% ; tar -xf deploy.tar ; rm deploy.tar ; sudo docker compose up -d --build"

del %TEMP%\oracle.key

echo.
echo ================================
echo ✅ Deployment Complete!
echo ================================
echo Backend:      http://%IP%:5000
echo Health Check: http://%IP%:5000/health
echo ================================
echo.
echo NOTE: If this is the first Docker installation,
echo you may need to SSH in and run 'newgrp docker'
echo or logout/login for Docker permissions.
goto end

:cleanup
del %TEMP%\oracle.key
echo.
echo ❌ Deployment failed!

:end

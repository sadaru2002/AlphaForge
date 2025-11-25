@echo off
echo Building and running container manually...

REM Create SSH key
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
echo -----BEGIN RSA PRIVATE KEY----- >> %TEMP%\oracle.key

echo.
echo [1/3] Building Docker image...
ssh -i %TEMP%\oracle.key ubuntu@161.118.218.33 "cd /opt/alphaforge ; sudo docker build -t alphaforge-backend ."

echo.
echo [2/3] Stopping old container (if any)...
ssh -i %TEMP%\oracle.key ubuntu@161.118.218.33 "sudo docker stop alphaforge-backend 2\u003e/dev/null ; sudo docker rm alphaforge-backend 2\u003e/dev/null"

echo.
echo [3/3] Starting new container...
ssh -i %TEMP%\oracle.key ubuntu@161.118.218.33 "sudo docker run -d --name alphaforge-backend --restart always -p 5000:5000 alphaforge-backend"

echo.
echo Checking container status...
ssh -i %TEMP%\oracle.key ubuntu@161.118.218.33 "sudo docker ps"

echo.
echo Checking logs...
ssh -i %TEMP%\oracle.key ubuntu@161.118.218.33 "sudo docker logs alphaforge-backend 2\u003e\u00261 | tail -50"

del %TEMP%\oracle.key

echo.
echo ================================================================================
echo ✅ Backend deployed!
echo ================================================================================
echo Health Check: http://161.118.218.33:5000/health
echo.
echo NOTE: If you can't access it, you need to open port 5000 in Oracle Cloud firewall
echo ================================================================================

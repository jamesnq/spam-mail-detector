@echo off
echo Installing Heroku CLI...

REM Download and install Heroku CLI
powershell -Command "& {Invoke-WebRequest https://cli-assets.heroku.com/heroku-x64.exe -OutFile heroku-installer.exe}"
heroku-installer.exe

echo.
echo Heroku CLI installed! Please follow these steps:

echo 1. Open a new command prompt and run: heroku login
echo 2. Run these commands to deploy:
echo    git init
echo    git add .
echo    git commit -m "Initial commit"
echo    heroku create spam-detector-app
echo    heroku config:set EMAIL=malcolmz3108@gmail.com
echo    heroku config:set PASSWORD=foiy qdrd bbss mgqr
echo    heroku config:set IMAP_SERVER=imap.gmail.com
echo    git push heroku main
echo.
echo Press any key to exit...
pause

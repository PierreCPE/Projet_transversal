from robotserver import RobotServer
import app
a = app.App()

app.runRobotServer(a.config, a.sharedVariables, a.sharedFrame)

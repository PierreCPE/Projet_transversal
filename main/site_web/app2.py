from robotserver import RobotServer
# import app
# a = app.App()

# app.runRobotServer(a.config, a.sharedVariables, a.sharedFrame)

robot_server = RobotServer()
spectre_moyen1 = robot_server.mode2Init()
for _ in range(12):
    robot_server.mode2Control(spectre_moyen1)


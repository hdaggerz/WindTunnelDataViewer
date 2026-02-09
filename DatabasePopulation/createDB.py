import sqlite3
con = sqlite3.connect("WindTunnel.db")
cur = con.cursor()
cur.execute("DROP TABLE IF EXISTS Run")
cur.execute("""
CREATE TABLE Run(
    id INTEGER PRIMARY KEY 
    , FileName TEXT
    , SheetName TEXT 
    , NRun INTEGER 
    , aFW FLOAT 
    , aRW FLOAT 
    , AmbientPressure FLOAT 
    , AmbientTemperature FLOAT 
    , FreeStreamVelocity FLOAT 
    , RoadSpeed FLOAT 
    , DynamicPressure FLOAT 
    , FrontLeftWheelDrag FLOAT 
    , FrontRightWheelDrag FLOAT
    , RearLeftWheelDrag FLOAT
    , RearRightWheelDrag FLOAT
    , BGurney BOOLEAN)""")



cur.execute("DROP TABLE IF EXISTS Test")
cur.execute("""
CREATE TABLE Test(
    id INTEGER PRIMARY KEY 
    , RunId INTEGER
    , FrontRideHeight FLOAT
    , RearRideHeight FLOAT
    , TotalDF FLOAT
    , FrontDF FLOAT
    , RearDF FLOAT
    , TotalDrag FLOAT
    , FrontWheelDrag FLOAT
    , RearWheelDrag FLOAT
    , Balance FLOAT
    , L_D FLOAT
    , SideForce FLOAT
    , YawMoment FLOAT
    , BodyDrag FLOAT)""")

cur.execute("""DROP VIEW IF EXISTS TestDetailed""")
cur.execute("""CREATE VIEW TestDetailed As 
	SELECT Run.aFW, 
	Run.aRW, 
	Test.FrontRideHeight,
	Test.RearRideHeight,
	Run.FreeStreamVelocity, 
	Run.RoadSpeed,
	Run.BGurney,
	Test.FrontDF,
	Test.RearDF,
	Test.TotalDF,
	Test.FrontWheelDrag,
	Test.RearWheelDrag,
	Test.BodyDrag,
	Test.Balance,
	Test.L_D	
	FROM Test INNER JOIN Run ON Test.RunId = Run.id""")
	
con.commit()

																														

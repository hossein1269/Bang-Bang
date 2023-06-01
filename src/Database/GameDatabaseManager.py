import sqlite3

class GameDatabaseManager:
    def __init__(self, DbName='bangBang.db') -> None:
        self.__connection = sqlite3.connect(f"./Database/{DbName}")
        self.__cursor = self.__connection.cursor()
    
    def GetHighScore(self) -> tuple[str,int]:
        """
        return High Score return (PlayerName, Score)
        """
        query = "SELECT Name,max(Score) FROM Players"
        return self.__cursor.execute(query).fetchone()
    

    def CheckPlayerNameExist(self, name) -> int:
        """
        Check Player Name Exsit If Exist Return Player Id else
        Call AddNewPlayer Then Call Itself
        """
        query = f"SELECT * FROM Players WHERE Name='{name}'"
        result = self.__cursor.execute(query).fetchall()
        if len(result) < 1:
            self.AddNewPlayer(name)
            return self.CheckPlayerNameExist(name)
        return result[0][0]
    
    def AddNewPlayer(self, name):
        query = f"INSERT INTO Players(Name,Score) VALUES('{name}',0)"
        self.__cursor.execute(query)
        self.__connection.commit()
    
    def UpdateScore(self, id, score):
        """
        Update Score To New Value And Return None
        """
        query = f"UPDATE Players SET Score={score} WHERE Id={id}"
        self.__cursor.execute(query)
        self.__connection.commit()

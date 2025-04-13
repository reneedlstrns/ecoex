class UserModel:
    def __init__(self, user_id, nick_name, email):
        self.id = user_id
        self.name = nick_name
        self.email = email

    def to_dict(self):
        return {
            'user_id': self.id,
            'nick_name': self.name,
            'email': self.email,
        }

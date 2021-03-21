users = []

class User ():
	def __init__ (self, id, iat, name, role, username)
		self.id = id
		self.iat = iat
		self.name = name
		self.role = role
		self.username = username

		self.password = None

	def __str__ (self):
		return f'User: \n\t{self.id} \n\t{self.name} \n\t{self.username} \n\t{self.role}'

def user_add (user):
	users.append (user)

def user_get_by_username (username):
	for u in users:
		if u.username == username:
			return u
	
	return None

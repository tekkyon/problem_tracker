import streamlit_authenticator as stauth
hashed_passwords = stauth.Hasher(['h4rdFuck']).generate()
print(hashed_passwords)
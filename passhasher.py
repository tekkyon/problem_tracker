import streamlit_authenticator as stauth
hashed_passwords = stauth.Hasher(['testpassword123']).generate()
print(hashed_passwords)
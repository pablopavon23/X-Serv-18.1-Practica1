#!/usr/bin/python3

import webapp
import csv
import urllib
import urllib.parse


class recortarURLs(webapp.webApp):
	#Creo mis dos diccionarios a utilizar
	diccionario_URLs_reales = {}
	diccionario_URLs_acortadas = {}

	try:		#abro mi fichero csv para consultar las que ya habia metidas
		with open('redireccion.csv') as csvfile:
			leefich = csv.reader(csvfile)
			for row in leefich:
				Url_acortada = row[0]
				Url_real = row[1]
				diccionario_URLs_reales[Url_real] = Url_acortada	#este diccionario contiene clave url real y valor url acortada
				diccionario_URLs_acortadas[Url_acortada] = Url_real		#este diccionario contiene clave url acortada y valor url real

	except:		#si no tengo ningun fichero csv aun es porque es la primera vez que la uso, luego lo creo
		cvsfile = open('redireccion.csv', 'w')
		csvfile.close()
#-------------------------------------------------------------------------------
	def parse(self, request):
		#Cojo el metodo, GET, PUT O POST
		metodo = request.split(' ',2)[0]
		#Cojo el recurso, que si no pongo nada despues de localhost:1234 lo tomare como si fuera un /
		try:
			recurso = request.split(' ',2)[1]
		except:
			recurso = "/"
		#Cojo el cuerpo de mi peticion
		try:
			solicitud = request.split('\r\n\r\n')[1]
		except IndexError:
			solicitud = ""

		return(metodo, recurso, solicitud)
#-------------------------------------------------------------------------------
	def process(self, peticion):
		metodo, recurso, solicitud = peticion
		if metodo == "GET":
			if (recurso != '/'):
				Url_busqueda = 'http://localhost:1234' + str(recurso)
				try:
					Url_redireccion = self.diccionario_URLs_acortadas[Url_busqueda]
					httpCode = "200 OK"
					htmlBody = '<html><head><meta http-equiv="Refresh" content="5;url='+ Url_redireccion +'"></head>' \
						+ "<body><h1> Espere a ser redirigido " \
						+ "</h1></body></html>"
				except KeyError:
					httpCode = "200 OK"
					htmlBody = "<html><body>" \
					+ 'Recurso no valido. Pruebe con localhost:1234/numerodepagina' \
					+ "</body></html>"


			else:

				httpCode = "200 OK"
				htmlBody = "<html><body>"  \
					+ '<form method="POST" action="">' \
					+ 'URL: <input type="text" name="url"><br>' \
					+ '<input type="submit" value="Enviar"><br>' \
					+ '</form>' \
					+ "</body></html>"

				for clave, valor in self.diccionario_URLs_reales.items():
					htmlBody = htmlBody + '<html><body><a href="'+ clave +'">' + clave + ' </a></br></body></html>' \
					+ '<html><body><a href="'+ valor +'">'+ valor + ' </a></br></body></html>'


		elif metodo == "PUT" or metodo == "POST":
			if solicitud != "":

				Url_nueva = solicitud.split("=")[1]
				Url_nueva = urllib.parse.unquote(Url_nueva, encoding='utf-8', errors='replace')
				http = Url_nueva.split("://")[0]

				if (http != 'http') and (http != 'https'):
					Url_nueva = 'https://' + Url_nueva

				try:
					Url_corta = self.diccionario_URLs_reales[Url_nueva]
					httpCode = "200 OK"
					htmlBody = "<html><body><h1> Esta URL ya ha sido acortada " \
					+ "</h1></body></html>" \
					+ "\r\n" \
					+'<html><body><a href="'+ Url_nueva +'">' + Url_nueva + ' </a></br></body></html>'\
					+ '<html><body><a href="'+ Url_corta +'">'+ Url_corta + ' </a></br></body></html>'

				except KeyError:
					contador = len(self.diccionario_URLs_reales)
					Url_corta_nueva = 'http://localhost:1234/' + str(contador)
					self.diccionario_URLs_reales[Url_nueva] = Url_corta_nueva
					self.diccionario_URLs_acortadas[Url_corta_nueva] = Url_nueva
					with open ('redireccion.csv', 'a') as csvfile:
						introducir_nueva = csv.writer(csvfile)
						introducir_nueva.writerow([Url_corta_nueva,Url_nueva])
					httpCode = "200 OK"
					htmlBody = "<html><body>Se ha acortado la URL de forma correcta</br>" \
					+'<a href="'+ Url_nueva +'">' + Url_nueva + ' </a></br>'\
					+ '<a href="'+ Url_corta_nueva +'">'+ Url_corta_nueva + ' </a></br></body></html>'

			else:
				httpCode = "200 OK"
				htmlBody = "<html><body>" \
				+ 'ERROR:  URL NO VALIDA.' \
				+ "</body></html>"

		else:
			httpCode = "450 Metodo no valido"
			htmlBody = " "
		return (httpCode, htmlBody)


if __name__ == "__main__":
	myWebApp = recortarURLs("localhost", 1234)

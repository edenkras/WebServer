import webserver.admin.views as views
from webserver.url import url

urls = [
	url('^/admin$', views.admin),
	url('^/admin-login$', views.login),
	url('^/admin-create-table$', views.createTable),
]

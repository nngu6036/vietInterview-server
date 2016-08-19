from openerp import models, fields, api,tools
from openerp.osv import osv
from openerp.service import common
from .. import util
class Country(models.Model):
	_name = 'res.country'
	_inherit = 'res.country'

	@api.model
	def getCountry(self):
		countries = self.env['res.country'].search([])
		countryList = [{'id' :c.id ,'title' :c.name} for c in countries]
		return countryList

class Province(models.Model):
	_name = 'res.country.state'
	_inherit = 'res.country.state'

	@api.model
	def getProvince(self):
		states = self.env['res.country.state'].search([])
		provinceList = [{'id' :s.id ,'title' :s.name ,'countryId' :s.country_id.id} for s in states]
		return provinceList

class EducationLevel(models.Model):
	_name = 'hr.recruitment.degree'
	_inherit = 'hr.recruitment.degree'

	@api.model
	def getEducationLevel(self ,lang):
		lang = util.lang_resolver(lang)
		context = {'lang' :lang}
		levels = self.env['hr.recruitment.degree'].with_context(context).search([])
		levelList = [{'id' :l.id ,'title' :l.name} for l in levels]
		return levelList
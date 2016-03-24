__author__ = 'Sergey'
from models import PostModel, OrganizationModel, TagsModel

orgs = OrganizationModel.query(OrganizationModel.category == u'Пиво')
for org in orgs:
    org.category = u'Пиво разливное'
    org.put()
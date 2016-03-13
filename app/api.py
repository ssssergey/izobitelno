import endpoints
from protorpc import remote
from models import OrganizationModel


@endpoints.api(name='organizationsAPI', version='v1', description='API for Managing Organizations')
class OrganizationsApi(remote.Service):
    @OrganizationModel.method(name='organizationAPI.insert', path='org')
    def insert_org(self, org):
        # request.author = endpoints.get_current_user()
        org.put()
        return org
    @OrganizationModel.query_method(name='organizationAPI.list', path='orgs')
    def get_org(self, query):
        return query

application_API = endpoints.api_server([OrganizationsApi])
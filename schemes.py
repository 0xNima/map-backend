from webservice import ma


class UsersSchema(ma.Schema):
    class Meta:
        fields = ('email', 'password')


class UsersReadSchema(ma.Schema):
    class Meta:
        fields = ('id', 'email', 'password', 'name', 'created_at', 'logged_out')


class CountriesSchema(ma.Schema):
    class Meta:
        fields = ('id', 'code', 'name')


class IndicatorsSchema(ma.Schema):
    class Meta:
        fields = ('id', 'type', 'name')


class ProjectsSchema(ma.Schema):
    class Meta:
        fields = ('name', 'description', 'thumbnail', 'geo_data_file', 'country_id')


class ProjectsReadSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'description', 'created_at', 'thumbnail', 'geo_data_file', 'country_id',
                  'query_report_url', 'query_start_date', 'query_end_date', 'query_indicator_id')


class ProjectReadSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'description', 'created_at', 'thumbnail', 'geo_data_file', 'country_id', 'report_url',
                  'query_report_url', 'query_start_date', 'query_end_date', 'query_indicator_id')


class QuerySchema(ma.Schema):
    class Meta:
        fields = ('indicator', 'url', 'start_date', 'end_date')


countries_schema = CountriesSchema(many=True)
indicators_schema = IndicatorsSchema(many=True)
user_schema = UsersSchema()
user_read_schema = UsersReadSchema()
projects_schema = ProjectsSchema()
projects_read_schema = ProjectsReadSchema(many=True)
project_read_schema = ProjectReadSchema()
query_schema = QuerySchema()

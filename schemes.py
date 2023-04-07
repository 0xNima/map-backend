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


countries_schema = CountriesSchema(many=True)
indicators_schema = IndicatorsSchema(many=True)
user_schema = UsersSchema()
user_read_schema = UsersReadSchema()

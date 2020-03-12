import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth import get_user_model
from graphql import GraphQLError


class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()


class Query(graphene.ObjectType):
    users = graphene.List(UserType)
    me = graphene.Field(UserType)

    def resolve_users(self, info):
        return get_user_model().objects.all()

    def resolve_me(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("not logged in")
        return user


class CreateUser(graphene.Mutation):
    created_user = graphene.Field(UserType)

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String(required=True)

    def mutate(self, info, username, email, password):
        user = get_user_model()(
            username=username,
            email=email
        )
        user.set_password(password)
        user.save()
        return CreateUser(created_user=user)


class UpdateUser(graphene.Mutation):
    updated_user = graphene.Field(UserType)

    class Arguments:
        username = graphene.String(required=False)
        password = graphene.String(required=False)
        email = graphene.String(required=False)

    def mutate(self, info, username='', password='', email=''):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("not authorized ")
        if username:
            user.username = username
        if email:
            user.email = email
        if password:
            user.set_password(password)
        user.save()
        return UpdateUser(updated_user=user)


class DeleteUser(graphene.Mutation):
    deleted_user = graphene.Field(UserType)

    def mutate(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("not authorized ")
        user.delete()
        return DeleteUser(deleted_user=user)


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()
    delete_user = DeleteUser.Field()

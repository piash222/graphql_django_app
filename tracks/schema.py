import graphene
from graphene_django import DjangoObjectType
from .models import Track


class TrackType(DjangoObjectType):
    class Meta:
        model = Track


class Query(graphene.ObjectType):
    tracks = graphene.List(TrackType)

    def resolve_tracks(self, info):
        return Track.objects.all()


class CreateTrack(graphene.Mutation):
    created_track = graphene.Field(TrackType)

    class Arguments:
        title = graphene.String(required=True)
        Description = graphene.String(required=True)
        url = graphene.String(required=True)

    def mutate(self, info, title, url, description):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('not logged in')

        track = Track.objects.create(posted_by=user, title=title, url=url, description=description)
        return CreateTrack(created_track=track)


class UpdateTrack(graphene.Mutation):
    updated_track = graphene.Field(TrackType)

    class Arguments:
        id = graphene.ID(required=True)
        title = graphene.String(required=False)
        Description = graphene.String(required=False)
        url = graphene.String(required=False)

    def mutate(self, info, id, title='', description='', url=''):
        user = info.context.user
        track = Track.objects.get(pk=id)
        if track.posted_by != user:
            raise Exception('raise exception')
        if track:
            track.title = title
        if description:
            track.description = description
        if url:
            track.url = url
        track.save()
        return UpdateTrack(updated_track=track)


class DeleteTrack(graphene.Mutation):
    deleted_track = graphene.Field(TrackType)

    class Arguments:
        id = graphene.ID(required=True)

    def mutate(self, info, id):
        user = info.context.user
        track = Track.objects.get(pk=id)
        if track.posted_by != user:
            raise Exception("not logged in")
        track.delete()
        return DeleteTrack(deleted_track=track)


class Mutation(graphene.ObjectType):
    create_track = CreateTrack.Field()
    update_track = UpdateTrack.Field()
    delete_track = DeleteTrack.Field()

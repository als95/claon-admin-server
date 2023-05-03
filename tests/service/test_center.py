import uuid
from datetime import datetime
from typing import List
from unittest.mock import AsyncMock

import pytest
from fastapi_pagination import Params, Page
from sqlalchemy.ext.asyncio import AsyncSession

from claon_admin.common.enum import WallType, Role
from claon_admin.common.error.exception import BadRequestException, UnauthorizedException, ErrorCode
from claon_admin.common.util.pagination import PaginationFactory, Pagination
from claon_admin.model.post import PostBriefResponseDto
from claon_admin.schema.center import CenterRepository, Center, CenterImage, OperatingTime, Utility, CenterFeeImage, \
    Post, PostImage, ClimbingHistory, PostRepository, CenterHold, CenterWall
from claon_admin.schema.user import User
from claon_admin.service.center import CenterService


@pytest.fixture
def mock_repo():
    center_repository = AsyncMock(spec=CenterRepository)
    post_repository = AsyncMock(spec=PostRepository)
    pagination_factory = AsyncMock(spec=PaginationFactory)

    return {
        "center": center_repository,
        "post": post_repository,
        "pagination_factory": pagination_factory
    }


@pytest.fixture
def center_service(mock_repo: dict):
    return CenterService(
        mock_repo["center"],
        mock_repo["post"],
        mock_repo["pagination_factory"]
    )


@pytest.fixture
def mock_user():
    yield User(
        id=str(uuid.uuid4()),
        oauth_id="oauth_id",
        nickname="nickname",
        profile_img="profile_img",
        sns="sns",
        email="test@test.com",
        instagram_name="instagram_name",
        role=Role.CENTER_ADMIN
    )


@pytest.fixture
def mock_pending_user():
    yield User(
        id=str(uuid.uuid4()),
        oauth_id="pending_oauth_id",
        nickname="pending_nickname",
        profile_img="pending_profile_img",
        sns="pending_sns",
        email="pending_test@test.com",
        instagram_name="pending_instagram_name",
        role=Role.PENDING
    )


@pytest.fixture
def mock_center(mock_user: User):
    yield Center(
        id=str(uuid.uuid4()),
        user=mock_user,
        name="test center",
        profile_img="https://test.profile.png",
        address="test_address",
        detail_address="test_detail_address",
        tel="010-1234-5678",
        web_url="http://test.com",
        instagram_name="test_instagram",
        youtube_url="https://www.youtube.com/@test",
        center_img=[CenterImage(url="https://test.image.png")],
        operating_time=[OperatingTime(day_of_week="월", start_time="09:00", end_time="18:00")],
        utility=[Utility(name="test_utility")],
        fee_img=[CenterFeeImage(url="https://test.fee.png")],
        approved=False
    )


@pytest.fixture
def mock_another_center(mock_pending_user: User):
    yield Center(
        id=str(uuid.uuid4()),
        user=mock_pending_user,
        name="another test center",
        profile_img="https://another.test.profile.png",
        address="another_test_address",
        detail_address="another_test_detail_address",
        tel="010-1234-3333",
        web_url="http://another.test.com",
        instagram_name="another_instagram",
        youtube_url="https://www.another.youtube.com/@test",
        center_img=[CenterImage(url="https://another.test.image.png")],
        operating_time=[OperatingTime(day_of_week="월", start_time="09:00", end_time="18:00")],
        utility=[Utility(name="another_utility")],
        fee_img=[CenterFeeImage(url="https://another.test.fee.png")],
        approved=False
    )


@pytest.fixture
def mock_center_holds(mock_center: Center):
    yield [
        CenterHold(
            id=str(uuid.uuid4()),
            center=mock_center,
            name="hold",
            difficulty="hard",
            is_color=False,
            img="hold_url"
        )
    ]


@pytest.fixture
async def mock_center_walls(session: AsyncSession, mock_center: Center):
    yield [
        CenterWall(
            id=str(uuid.uuid4()),
            center=mock_center,
            name="wall",
            type=WallType.ENDURANCE.value
        )
    ]


@pytest.fixture
def mock_post(mock_user: User, mock_center: Center):
    yield Post(
        id=str(uuid.uuid4()),
        user=mock_user,
        center=mock_center,
        content="content",
        created_at=datetime(2023, 2, 3),
        img=[PostImage(url="https://test.post.img.png")]
    )


@pytest.fixture
def mock_climbing_history(mock_post: Post, mock_center_holds: List[CenterHold], mock_center_walls: List[CenterWall]):
    yield [
        ClimbingHistory(
            id=str(uuid.uuid4()),
            post=mock_post,
            hold_id=mock_center_holds[0].id,
            hold_url=mock_center_holds[0].img,
            difficulty=mock_center_holds[0].difficulty,
            challenge_count=3,
            wall_name=mock_center_walls[0].name,
            wall_type=mock_center_walls[0].type)
    ]


@pytest.mark.asyncio
async def test_find_posts_by_center_without_hold(session: AsyncSession,
                                                 mock_repo: dict,
                                                 mock_center: Center,
                                                 mock_post: Post,
                                                 center_service: CenterService):
    # given
    params = Params(page=1, size=10)
    post_page = Page(items=[mock_post], params=params, total=1)
    mock_repo["center"].find_by_id.side_effect = [mock_center]
    mock_repo["post"].find_posts_by_center.side_effect = post_page
    mock_pagination = Pagination(
        next_page_num=2,
        previous_page_num=0,
        total_num=1,
        results=[PostBriefResponseDto.from_entity(mock_post)]
    )
    mock_repo["pagination_factory"].create.side_effect = [mock_pagination]

    # when
    pages: Pagination[PostBriefResponseDto] = await center_service.find_posts_by_center(
        session=session,
        params=params,
        center_id=mock_center.id,
        hold_id=None,
        start=datetime(2022, 4, 1),
        end=datetime(2023, 3, 31)
    )

    # then
    assert len(pages.results) == 1
    assert pages.results[0].post_id == mock_post.id
    assert pages.results[0].content == mock_post.content
    assert pages.results[0].image == mock_post.img[0].url
    assert pages.results[0].created_at == mock_post.created_at.strftime("%Y-%m-%d %H:%M:%S")
    assert pages.results[0].user_id == mock_post.user.id
    assert pages.results[0].user_nickname == mock_post.user.nickname


@pytest.mark.asyncio
async def test_find_posts_by_center_with_hold(session: AsyncSession,
                                              mock_repo: dict,
                                              mock_center: Center,
                                              mock_climbing_history: List[ClimbingHistory],
                                              mock_post: Post,
                                              center_service: CenterService):
    # given
    params = Params(page=1, size=10)
    post_page = Page(items=[mock_post], params=params, total=1)
    mock_repo["center"].find_by_id.side_effect = [mock_center]
    mock_repo["post"].find_posts_by_center.side_effect = post_page
    mock_pagination = Pagination(
        next_page_num=2,
        previous_page_num=0,
        total_num=1,
        results=[PostBriefResponseDto.from_entity(mock_post)]
    )
    mock_repo["pagination_factory"].create.side_effect = [mock_pagination]

    # when
    pages: Pagination[PostBriefResponseDto] = await center_service.find_posts_by_center(
        session,
        params,
        mock_center.id,
        mock_climbing_history[0].hold_id,
        datetime(2022, 4, 1),
        datetime(2023, 3, 31)
    )

    # then
    assert len(pages.results) == 1
    assert pages.results[0].post_id == mock_post.id
    assert pages.results[0].content == mock_post.content
    assert pages.results[0].image == mock_post.img[0].url
    assert pages.results[0].created_at == mock_post.created_at.strftime("%Y-%m-%d %H:%M:%S")
    assert pages.results[0].user_id == mock_post.user.id
    assert pages.results[0].user_nickname == mock_post.user.nickname


@pytest.mark.asyncio
async def test_find_posts_by_center_with_wrong_center_id(session: AsyncSession,
                                                         mock_repo: dict,
                                                         center_service: CenterService):
    # given
    center_id = "not_existing_id"
    mock_repo["center"].find_by_id.side_effect = [None]
    params = Params(page=1, size=10)

    with pytest.raises(BadRequestException) as exception:
        # when
        await center_service.find_posts_by_center(
            session,
            params,
            center_id,
            None,
            datetime(2022, 4, 1),
            datetime(2023, 3, 31)
        )

    # then
    assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST


@pytest.mark.asyncio
async def test_find_posts_by_center_not_included_hold_in_center(session: AsyncSession,
                                                                mock_repo: dict,
                                                                mock_center: Center,
                                                                center_service: CenterService):
    # given
    mock_repo["center"].find_by_id.side_effect = [mock_center]
    params = Params(page=1, size=10)

    with pytest.raises(BadRequestException) as exception:
        # when
        await center_service.find_posts_by_center(
            session,
            params,
            mock_center.id,
            "not included hold",
            datetime(2022, 4, 1),
            datetime(2023, 3, 31)
        )

    # then
    assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST


@pytest.mark.asyncio
async def test_find_posts_by_center_not_center_admin(session: AsyncSession,
                                                     mock_repo: dict,
                                                     mock_another_center: Center,
                                                     mock_climbing_history: ClimbingHistory,
                                                     center_service: CenterService):
    # given
    mock_repo["center"].find_by_id.side_effect = [mock_another_center]
    params = Params(page=1, size=10)

    with pytest.raises(UnauthorizedException) as exception:
        # when
        await center_service.find_posts_by_center(
            session,
            params,
            mock_another_center.id,
            mock_climbing_history[0].hold_id,
            datetime(2022, 4, 1),
            datetime(2023, 3, 31)
        )

    # then
    assert exception.value.code == ErrorCode.NOT_ACCESSIBLE
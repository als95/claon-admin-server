import pytest

from claon_admin.common.enum import Role
from claon_admin.common.error.exception import NotFoundException, ErrorCode, UnauthorizedException
from claon_admin.model.auth import RequestUser
from claon_admin.model.review import ReviewAnswerRequestDto
from claon_admin.schema.center import Center, Review, ReviewAnswer
from claon_admin.service.center import CenterService


@pytest.mark.describe("Test case for create review answer")
class TestCreateReviewAnswer(object):
    @pytest.mark.asyncio
    @pytest.mark.it("Success case")
    async def test_create_review_answer(
            self,
            center_service: CenterService,
            mock_repo: dict,
            center_fixture: Center,
            not_answered_review_fixture: Review,
            new_review_answer_fixture: ReviewAnswer
    ):
        # given
        request_user = RequestUser(id=center_fixture.user.id, sns="test@claon.com", role=Role.CENTER_ADMIN)
        dto = ReviewAnswerRequestDto(
            answer_content="new answer"
        )

        mock_repo["center"].find_by_id.side_effect = [center_fixture]
        mock_repo["review"].find_by_id_and_center_id.side_effect = [not_answered_review_fixture]
        mock_repo["review_answer"].find_by_review_id.side_effect = [None]
        mock_repo["review_answer"].save.side_effect = [new_review_answer_fixture]

        # when
        result = await center_service.create_review_answer(
            None,
            request_user,
            dto,
            center_fixture.id,
            not_answered_review_fixture.id
        )

        # then
        assert result.review_id == not_answered_review_fixture.id

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: center is not found")
    async def test_create_review_answer_with_not_exist_center(
            self,
            center_service: CenterService,
            mock_repo: dict,
            center_fixture: Center,
            review_fixture: Review
    ):
        # given
        request_user = RequestUser(id=center_fixture.user.id, sns="test@claon.com", role=Role.CENTER_ADMIN)
        mock_repo["center"].find_by_id.side_effect = [None]
        wrong_id = "wrong id"
        dto = ReviewAnswerRequestDto(answer_content="content")

        with pytest.raises(NotFoundException) as exception:
            # when
            await center_service.create_review_answer(None, request_user, dto, wrong_id, review_fixture.id)

        # then
        assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: request user is not center admin")
    async def test_create_review_answer_with_not_center_admin(
            self,
            center_service: CenterService,
            mock_repo: dict,
            center_fixture: Center,
            review_fixture: Review
    ):
        # given
        request_user = RequestUser(id="123456", sns="test@claon.com", role=Role.CENTER_ADMIN)
        mock_repo["center"].find_by_id.side_effect = [center_fixture]
        dto = ReviewAnswerRequestDto(answer_content="content")

        with pytest.raises(UnauthorizedException) as exception:
            # when
            await center_service.create_review_answer(None, request_user, dto, center_fixture.id, review_fixture.id)

        # then
        assert exception.value.code == ErrorCode.NOT_ACCESSIBLE

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: review is not found")
    async def test_create_review_answer_with_not_exist_review(
            self,
            center_service: CenterService,
            mock_repo: dict,
            center_fixture: Center
    ):
        # given
        request_user = RequestUser(id=center_fixture.user.id, sns="test@claon.com", role=Role.CENTER_ADMIN)
        mock_repo["center"].find_by_id.side_effect = [center_fixture]
        mock_repo["review"].find_by_id_and_center_id.side_effect = [None]
        dto = ReviewAnswerRequestDto(answer_content="content")
        wrong_review_id = "wrong id"

        with pytest.raises(NotFoundException) as exception:
            # when
            await center_service.create_review_answer(None, request_user, dto, center_fixture.id, wrong_review_id)

        # then
        assert exception.value.code == ErrorCode.DATA_DOES_NOT_EXIST

    @pytest.mark.asyncio
    @pytest.mark.it("Fail case: review is already answered")
    async def test_create_review_answer_with_already_exist_answer(
            self,
            center_service: CenterService,
            mock_repo: dict,
            center_fixture: Center,
            review_fixture: Review,
            review_answer_fixture: ReviewAnswer
    ):
        # given
        request_user = RequestUser(id=center_fixture.user.id, sns="test@claon.com", role=Role.CENTER_ADMIN)
        mock_repo["center"].find_by_id.side_effect = [center_fixture]
        mock_repo["review"].find_by_id_and_center_id.side_effect = [review_fixture]
        mock_repo["review_answer"].find_by_review_id.side_effect = [review_answer_fixture]
        dto = ReviewAnswerRequestDto(answer_content="content")

        with pytest.raises(NotFoundException) as exception:
            # when
            await center_service.create_review_answer(None, request_user, dto, center_fixture.id, review_fixture.id)

        # then
        assert exception.value.code == ErrorCode.ROW_ALREADY_EXIST

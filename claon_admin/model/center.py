import re
from typing import Optional, List

from pydantic import BaseModel, validator

from claon_admin.config.consts import KOR_BEGIN_CODE, KOR_END_CODE
from claon_admin.model.enum import WallType
from claon_admin.model.user import UserProfileDto


class CenterOperatingTimeDto(BaseModel):
    day_of_week: str
    start_time: str
    end_time: str

    @validator('day_of_week')
    def validate_day_of_week(cls, value):
        if value not in ['월', '화', '수', '목', '금', '토', '일', '공휴일']:
            raise ValueError('요일은 월, 화, 수, 목, 금, 토, 일 중 하나로 입력 해주세요.')
        return value

    @validator('start_time')
    def validate_start_time(cls, value):
        if not re.match(r'^(0\d|1\d|2[0-3]):(0[1-9]|[0-5]\d)$', value):
            raise ValueError('올바른 시간 형식으로 입력 해주세요.')
        return value

    @validator('end_time')
    def validate_end_time(cls, value):
        if not re.match(r'^(0\d|1\d|2[0-3]):(0[1-9]|[0-5]\d)$', value):
            raise ValueError('올바른 시간 형식으로 입력 해주세요.')
        return value


class CenterFeeDto(BaseModel):
    name: str
    price: int
    count: int

    @validator('name')
    def validate_name(cls, value):
        if len(value) < 2 or len(value) > 50:
            raise ValueError('이름은 2자 이상 50자 이하로 입력 해주세요.')
        return value

    @validator('price')
    def validate_price(cls, value):
        if value < 0:
            raise ValueError('가격은 0원 이상으로 입력 해주세요.')
        return value

    @validator('count')
    def validate_count(cls, value):
        if value < 0:
            raise ValueError('횟수는 0회 이상으로 입력 해주세요.')
        return value


class CenterHoldDto(BaseModel):
    difficulty: str
    name: str

    @validator('difficulty')
    def validate_difficulty(cls, value):
        if len(value) < 2 or len(value) > 10:
            raise ValueError('홀드 난이도는 1자 이상 10자 이하로 입력 해주세요.')
        return value

    @validator('name')
    def validate_name(cls, value):
        if len(value) < 2 or len(value) > 10:
            raise ValueError('홀드 이름은 1자 이상 10자 이하로 입력 해주세요.')
        return value


class CenterWallDto(BaseModel):
    wall_type: WallType
    name: str

    @validator('name')
    def validate_name(cls, value):
        if len(value) < 2 or len(value) > 20:
            raise ValueError('벽 이름은 2자 이상 20자 이하로 입력 해주세요.')
        return value


class CenterNameResponseDto(BaseModel):
    center_id: str
    name: str
    address: str


class CenterResponseDto(BaseModel):
    profile_image: str
    name: str
    address: str
    detail_address: Optional[str]
    tel: str
    web_url: Optional[str]
    instagram_name: Optional[str]
    youtube_code: Optional[str]
    image_list: List[str]
    utility_list: List[str]
    fee_image_list: List[str]
    operating_time_list: List[CenterOperatingTimeDto]
    fee_list: List[CenterFeeDto]
    hold_list: List[CenterHoldDto]
    wall_list: List[CenterWallDto]


class CenterRequestDto(BaseModel):
    profile: UserProfileDto
    profile_image: str
    name: str
    address: str
    detail_address: Optional[str]
    tel: str
    web_url: Optional[str]
    instagram_name: Optional[str]
    youtube_code: Optional[str]
    image_list: List[str]
    utility_list: List[str]
    fee_image_list: List[str]
    operating_time_list: List[CenterOperatingTimeDto]
    fee_list: List[CenterFeeDto]
    hold_list: List[CenterHoldDto]
    wall_list: List[CenterWallDto]
    proof_list: List[str]

    @validator('name')
    def validate_name(cls, value):
        for c in value:
            if not (('a' <= c <= 'z') or ('A' <= c <= 'Z') or (
                    KOR_BEGIN_CODE <= ord(c) <= KOR_END_CODE) or c.isdigit()):
                raise ValueError('암장명은 한글, 영문, 숫자로만 입력 해주세요.')
        if len(value) < 2 or len(value) > 50:
            raise ValueError('암장명은 2자 이상 50자 이하로 입력 해주세요.')
        return value

    @validator('tel', pre=True, always=True)
    def validate_tel(cls, value):
        if not re.match(r'^(0)\d{1,2}-\d{3,4}-\d{4}$', value):
            raise ValueError('전화번호를 올바른 형식으로 다시 입력해주세요.')
        return value

    @validator('instagram_name')
    def validate_instagram_name(cls, value):
        if value is None:
            return value

        for c in value:
            if not (('a' <= c <= 'z') or ('A' <= c <= 'Z') or (
                    KOR_BEGIN_CODE <= ord(c) <= KOR_END_CODE) or c.isdigit()):
                raise ValueError('인스타그램 닉네임은 한글, 영문, 숫자로만 입력 해주세요.')
        if len(value) < 3 or len(value) > 30:
            raise ValueError('인스타그램 닉네임은 3자 이상 30자 이하로 입력 해주세요.')
        return value

    @validator('youtube_code')
    def validate_youtube_code(cls, value):
        if value is None:
            return value

        if value[0] != "@":
            raise ValueError('유튜브 채널 코드는 @로 시작 해주세요.')

    @validator('image_list')
    def validate_image_list(cls, value):
        if len(value) > 10:
            raise ValueError('이미지는 최대 10장까지 등록 가능해요.')
        return value

    @validator('fee_image_list')
    def validate_fee_image_list(cls, value):
        if len(value) > 5:
            raise ValueError('이용요금 이미지는 최대 10장까지 등록 가능해요.')
        return value

    @validator('operating_time_list')
    def validate_operating_time_list(cls, value):
        if len(value) > 8:
            raise ValueError('운영시간은 최대 8개까지 등록 가능해요.')
        return value

    @validator('proof_list')
    def validate_proof_list(cls, value):
        if len(value) > 5:
            raise ValueError('증빙자료는 5개 이하로 입력 해주세요.')
        return value


class UploadFileResponseDto(BaseModel):
    file_url: str
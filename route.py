from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel

from config import template, word_data
from models import User

main_router = APIRouter(prefix='/')


@main_router.get('/')
async def open_page(request: Request):
    user = await User.get_or_none(host=request.client.host)
    if user:
        level = user.data['level']
        word = list(word_data.keys())[level]
        response = template.TemplateResponse(request, 'home.html', {'length': len(word), 'max': word_data[word],
                                                                    'attempts': user.data['attempts'],
                                                                    'level': level + 1})
        response.context.update(user.data)
        return response
    else:
        word = list(word_data.keys())[0]
        response = template.TemplateResponse(request, 'home.html', {'length': len(word), 'max': word_data[word],
                                                                    'attempts': 0, 'level': 1})

        user = await User.create(host=request.client.host)
        response.context.update(user.data)
    return response


class GuessWord(BaseModel):
    guess_word: str


@main_router.post('/attempt')
async def guess_attempt(guess_word: GuessWord, request: Request):
    guess_word = guess_word.guess_word.lower()
    user = await User.get_or_none(host=request.client.host)
    if user:
        level = user.data['level']
        legal_word = list(word_data.keys())[level]
        context = {**user.data, 'length': len(legal_word), 'max': word_data[legal_word], }
        if user.data['attempts'] == word_data[legal_word]:
            return {'success': False, 'exist_indexes': [], 'correct_indexes': [],
                    'attempts': user.data['attempts'],
                    **context}
    else:
        raise HTTPException(401, 'Error! You are not authorized')
    user.data['attempts'] += 1
    user.data['guesses'].append(guess_word)
    await user.save()
    context = {**user.data, 'length': len(legal_word), 'max': word_data[legal_word]}
    if guess_word == legal_word:
        correct_indexes = list(range(len(legal_word)))
        for i in range(word_data[legal_word] - user.data['attempts']):
            user.data['guesses'].append('-' * len(legal_word))
        user.data['attempts'] = word_data[legal_word]
        await user.save()
        return {'success': True, 'correct_indexes': correct_indexes, 'exist_indexes': [], **context}
    else:
        exist_indexes = []
        correct_indexes = []
        i = 0
        for letter in guess_word:
            if letter in legal_word:
                if letter == legal_word[i]:
                    correct_indexes.append(i)
                else:
                    exist_indexes.append(i)
            i += 1
        return {'success': False, 'exist_indexes': exist_indexes, 'correct_indexes': correct_indexes,
                **context}


@main_router.get('/attempt')
async def get_attempts(request: Request):
    user = await User.get_or_none(host=request.client.host)
    if user:
        level = user.data['level']
        word = list(word_data.keys())[level]
        legal_word = word.lower()
        context = {'success': True, 'guesses': [], 'attempts': user.data['attempts']}
        for guess in user.data['guesses']:
            correct_indexes = []
            exist_indexes = []
            i = 0
            for letter in guess:
                if letter in legal_word:
                    if letter == legal_word[i]:
                        correct_indexes.append(i)
                    else:
                        exist_indexes.append(i)
                i += 1
            context['guesses'].append(
                {'guess': guess, 'exist_indexes': exist_indexes, 'correct_indexes': correct_indexes})
        return context
    else:
        raise HTTPException(401, 'Error! You are not authorized')


@main_router.get('/restart')
async def restart_game(request: Request):
    user = await User.get_or_none(host=request.client.host)
    await user.delete()


@main_router.get('/next')
async def next_word(request: Request):
    user = await User.get_or_none(host=request.client.host)
    user.data['attempts'] = 0
    user.data['guesses'] = []
    user.data['level'] += 1
    await user.save()

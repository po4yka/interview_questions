---
title: MVI Pattern (Model-View-Intent)
topic: architecture-patterns
subtopics:
  - android-architecture
  - unidirectional-data-flow
  - state-management
difficulty: hard
related:
  - mvvm-pattern
  - mvp-pattern
  - redux-architecture
status: reviewed
---

# MVI Pattern / Паттерн MVI (Model-View-Intent)

## English

### Definition
**MVI** stands for **Model-View-Intent**. MVI is one of the newest architecture patterns for Android, inspired by the unidirectional and cyclical nature of the Cycle.js framework.

MVI works in a very different way compared to its distant relatives, MVC, MVP or MVVM. The role of each MVI component is as follows:
- **Model** represents a state. Models in MVI should be immutable to ensure a unidirectional data flow between them and the other layers in your architecture
- Like in MVP, Interfaces in MVI represent **Views**, which are then implemented in one or more Activities or Fragments
- **Intent** represents an intention or a desire to perform an action, either by the user or the app itself. For every action, a View receives an Intent. The Presenter observes the Intent, and Models translate it into a new state

### MVI Workflow
The flow works as follows:
1. User interaction happens which will be an Intent
2. Intent is a state which is an input to model
3. Model stores state and sends the requested state to the View
4. View loads the state from Model
5. Updated UI is displayed to the user

### Advantages
Using this architecture brings the following benefits:
- **No state problem** anymore, because there is only one state for our app, which is a single source of truth
- **Unidirectional data flow**, which makes the logic of our app more predictable and easier to understand
- **Immutability** - as long as each output is an immutable object, we can take advantage of the benefits associated with immutability (thread safety or share-ability)
- **Debuggability** - unidirectional data flow ensures that our app is easy to debug. Every time we pass our data from one component to another, we can log the current value of the outflow. Thus, when we get a bug report, we can see the state our app was in when the error was made, and we can even see the user's intent under which this state was created
- **Decoupled logic**, because each component has its own responsibility
- **Testability** - all we have to do to write the unit test for our app is call a proper business method and check if we've got a proper state

### Disadvantages
However, nothing is perfect, and there are some drawbacks you should be aware of before using MVI:
- **A lot of boilerplate** - each small UI change has to start with a user's intent and then must pass the whole circle. Even with the easiest implementation, you have to create at least an intent and a state object for every action made in our app
- **Complexity** - there is a lot of logic inside which must be strictly followed, and there is a high probability that not everybody knows about it. This may cause problems especially when you need to expand your team as it will take more time for newcomers to get used to it
- **Object creation**, which is expensive. If too many objects are created, your heap memory can easily reach full capacity and then your garbage collector will be too busy. You should strike a balance between the structure and size of your app
- **SingleLiveEvents**. To create these with MVI architecture (for example displaying a snackbar message), you should have a state with `showMessage = true` attribute and render it by showing the snackbar. However, what if a config change comes into play? Then you should display the latest state, which would present the snackbar again. Although that's correct behavior, it is not so user friendly. We have to create another state telling us not to display the message again

### Key Principles
1. **Single Source of Truth**: There is only one state for the entire screen or feature
2. **Immutable State**: States cannot be modified once created
3. **Unidirectional Data Flow**: Data flows in one direction: Intent → Model → View
4. **Reactive Programming**: Often implemented using reactive streams (RxJava, Coroutines Flow)

### Use Cases in Android
- Complex UI with multiple state changes
- Applications requiring strict state management
- Apps where debugging state changes is critical
- Feature-rich applications with complex user interactions

---

## Русский

### Определение
**MVI** означает **Model-View-Intent** (Модель-Представление-Намерение). MVI - это один из новейших архитектурных паттернов для Android, вдохновленный однонаправленной и циклической природой фреймворка Cycle.js.

MVI работает совершенно иначе по сравнению со своими дальними родственниками MVC, MVP или MVVM. Роль каждого компонента MVI следующая:
- **Model (Модель)** представляет состояние. Модели в MVI должны быть неизменяемыми, чтобы обеспечить однонаправленный поток данных между ними и другими слоями в вашей архитектуре
- Как и в MVP, интерфейсы в MVI представляют **Views (Представления)**, которые затем реализуются в одной или нескольких Activity или Fragment
- **Intent (Намерение)** представляет намерение или желание выполнить действие, либо пользователем, либо самим приложением. Для каждого действия View получает Intent. Presenter наблюдает за Intent, а Models преобразуют его в новое состояние

### Рабочий Процесс MVI
Поток работает следующим образом:
1. Происходит взаимодействие пользователя, которое будет Intent
2. Intent - это состояние, которое является входом для модели
3. Модель сохраняет состояние и отправляет запрошенное состояние в View
4. View загружает состояние из Model
5. Обновленный UI отображается пользователю

### Преимущества
Использование этой архитектуры приносит следующие преимущества:
- **Больше нет проблем с состоянием**, потому что есть только одно состояние для нашего приложения, которое является единственным источником истины
- **Однонаправленный поток данных**, который делает логику нашего приложения более предсказуемой и легкой для понимания
- **Неизменяемость** - пока каждый выход является неизменяемым объектом, мы можем воспользоваться преимуществами, связанными с неизменяемостью (потокобезопасность или возможность совместного использования)
- **Отлаживаемость** - однонаправленный поток данных гарантирует, что наше приложение легко отлаживать. Каждый раз, когда мы передаем наши данные из одного компонента в другой, мы можем логировать текущее значение выходного потока. Таким образом, когда мы получаем отчет об ошибке, мы можем увидеть состояние, в котором находилось наше приложение, когда была сделана ошибка, и мы даже можем увидеть намерение пользователя, при котором это состояние было создано
- **Разделенная логика**, потому что каждый компонент имеет свою собственную ответственность
- **Тестируемость** - все, что нам нужно сделать, чтобы написать unit-тест для нашего приложения, это вызвать соответствующий бизнес-метод и проверить, получили ли мы правильное состояние

### Недостатки
Однако ничто не идеально, и есть некоторые недостатки, о которых вам следует знать перед использованием MVI:
- **Много шаблонного кода** - каждое небольшое изменение UI должно начинаться с намерения пользователя, а затем должно пройти весь круг. Даже при самой простой реализации вам нужно создать как минимум объект намерения и объект состояния для каждого действия, выполняемого в нашем приложении
- **Сложность** - внутри много логики, которой нужно строго следовать, и есть высокая вероятность, что не все об этом знают. Это может вызвать проблемы, особенно когда вам нужно расширить команду, так как новичкам потребуется больше времени, чтобы привыкнуть к этому
- **Создание объектов**, которое дорого. Если создается слишком много объектов, ваша куча памяти может легко достичь полной емкости, и тогда ваш сборщик мусора будет слишком занят. Вы должны найти баланс между структурой и размером вашего приложения
- **SingleLiveEvents**. Чтобы создать их с архитектурой MVI (например, отображение snackbar-сообщения), у вас должно быть состояние с атрибутом `showMessage = true` и отрендерить его, показав snackbar. Однако, что если происходит изменение конфигурации? Тогда вы должны отобразить последнее состояние, которое снова покажет snackbar. Хотя это правильное поведение, оно не очень удобно для пользователя. Мы должны создать другое состояние, говорящее нам не отображать сообщение снова

### Ключевые Принципы
1. **Единый источник истины**: Есть только одно состояние для всего экрана или функции
2. **Неизменяемое состояние**: Состояния не могут быть изменены после создания
3. **Однонаправленный поток данных**: Данные текут в одном направлении: Intent → Model → View
4. **Реактивное программирование**: Часто реализуется с использованием реактивных потоков (RxJava, Coroutines Flow)

### Примеры Использования в Android
- Сложный UI с множественными изменениями состояния
- Приложения, требующие строгого управления состоянием
- Приложения, где отладка изменений состояния критична
- Многофункциональные приложения со сложными пользовательскими взаимодействиями

---

## References
- [MVI Architecture for Android Tutorial: Getting Started - Kodeco](https://www.kodeco.com/817602-mvi-architecture-for-android-tutorial-getting-started)
- [Android MVI Architecture Example - Medium](https://krishanmadushankadev.medium.com/android-mvi-model-view-intent-architecture-example-code-bc7dc8edb33)
- [MVI — Another Member of the MV* Band - ProAndroidDev](https://proandroiddev.com/mvi-a-new-member-of-the-mv-band-6f7f0d23bc8a)
- [MVI with State-Machine - ProAndroidDev](https://proandroiddev.com/mvi-architecture-with-a-state-machine-basics-721c5ebed893)
- [Reactive Apps with Model-View-Intent](http://hannesdorfmann.com/android/mosby3-mvi-1/)
- [The Story of MVI](https://funkymuse.dev/posts/the-story-of-mvi/)
- [Getting Started with MVI Architecture on Android](https://ericampire.com/getting-started-with-mvi-architecture-on-android-b2c280b7023)
- [Best Architecture For Android: MVI + LiveData + ViewModel](https://proandroiddev.com/best-architecture-for-android-mvi-livedata-viewmodel-71a3a5ac7ee3)
- [MVI - The Good, the Bad, and the Ugly](https://adambennett.dev/2019/07/mvi-the-good-the-bad-and-the-ugly/)

---

**Source:** Kirchhoff-Android-Interview-Questions
**Attribution:** Content adapted from the Kirchhoff repository

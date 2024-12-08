import 'package:equatable/equatable.dart';
import '../../../core/app_export.dart';
import '../model/splash_model.dart';
import '../../../core/utils/navigator_service.dart';
part 'splash_event.dart';
part 'splash_state.dart';

// A bloc that manages the state of a Splash according to the event that is received
class SplashBloc extends Bloc<SplashEvent, SplashState> {
  SplashBloc(SplashState initialState) : super(initialState) {
    on<SplashInitialEvent>(_onInitialize);
  }

  _onInitialize(
    SplashInitialEvent event,
    Emitter<SplashState> emit,
  ) async {
    await Future.delayed(const Duration(milliseconds: 3000), () {
      NavigatorService.popAndPushNamed(
        AppRoutes.welcomeScreenRiderScreen,
      );
    });
  }
}

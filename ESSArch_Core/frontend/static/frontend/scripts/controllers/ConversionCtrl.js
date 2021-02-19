export default class ConversionCtrl {
  constructor($scope, $rootScope, appConfig, $translate, $http, $timeout, $uibModal) {
    const vm = this;
    vm.flowOptions = {};
    vm.options = {converters: []};
    vm.fields = $scope.mockedConversions;
    vm.activeTab = 'conversion0';
    vm.profiles = [];
    vm.arrlist = [];
    vm.saprofiles = [];
    var listA = []; 
    var listB = [];

    var listA = [];
    vm.profile = [];
    const ipToSearch = 'a44ad659-07f2-420c-aa80-f2d55df99970';
    
    $scope.dunit= vm.arrlist[0];
    vm.$onInit = function () {
      console.log('hello from change');
      console.log('index');
      console.log($scope.$index);

      vm.profilesLoading = true;
      
                $http({
                  url: appConfig.djangoUrl + 'profiles/',
                  method: 'GET',
                  params: {pager: 'none'},
                }).then(function (response) {
                  const pdata = response.data;
                  var profile = null;
                    for (var j = 0; j < pdata.length; j++) {
                      if (pdata[j].profile_type.includes('validation')) {
                        
                        profile = {
                          id: pdata[j].id,
                          name: pdata[j].name,
                        }
      
                        listA.push(profile);
                      }
                    }
                  
                  vm.profilesLoading = false;
                })
              .catch(() => {
                vm.profilesLoading = false;
              });
            
             
          
      $http({
        url: appConfig.djangoUrl + 'profile-ip/',
        method: 'GET',
        params: {pager: 'none'},
      })
        .then(function (response) {
          const pdata = response.data;
          var profile = null;
          for (var j = 0; j < pdata.length; j++) {
            if(pdata[j].ip.includes(ipToSearch)){
              profile = {
                id: pdata[j].id,
                name: pdata[j].profile_name,
                profile_type: pdata[j].profile_type,
              }
            }
          listB.push(profile);

        }
      })
        .catch(() => {
          console.log('catch ');
        });

      console.log('Profiles list');
      console.log(listB);
      
      vm.arrlist = listA;
      vm.saprofiles = listB;
      
    };

    vm.purposeField = [
      {
        key: 'purpose',
        type: 'input',
        templateOptions: {
          label: $translate.instant('PURPOSE'),
        },
      },
    ];

    let tabNumber = 0;
    vm.conversions = [
      {
        id: 0,
        name: '1',
        converter: null,
        data: {},
      },
    ];

    vm.currentConversion = vm.conversions[0];
    vm.updateConverterForm = (conversion) => {
      vm.currentConversion = conversion;
      if (conversion.converter) {
        vm.fields = conversion.converter.form;
      } else {
        vm.fields = [];
      }
    };

    vm.getConverters = function (search) {
      return $http({
        url: appConfig.djangoUrl + 'action-tools/',
        method: 'GET',
        params: {search: search, pager: 'none'},
      }).then(function (response) {
        vm.options.converters = response.data.map((converter) => {
          return converter;
        });
        return vm.options.converters;
      });
    };

    vm.addConverter = () => {
      tabNumber++;
      let val = {
        id: tabNumber,
        name: tabNumber + 1,
        validator: null,
        data: {},
      };
      vm.conversions.push(val);
      $timeout(() => {
        vm.activeTab = 'conversion' + tabNumber;
        vm.updateConverterForm(val);
      });
    };

    vm.removeConversionModal = (conversion) => {
      var modalInstance = $uibModal.open({
        animation: true,
        ariaLabelledBy: 'modal-title',
        ariaDescribedBy: 'modal-body',
        templateUrl: 'static/frontend/views/remove_conversion_modal.html',
        scope: $scope,
        controller: 'RemoveConversionModalInstanceCtrl',
        controllerAs: '$ctrl',
        resolve: {
          data: {
            conversion,
          },
        },
      });
      modalInstance.result.then(
        () => {
          vm.conversions.forEach((x, index, array) => {
            if (x.id === conversion.id) {
              array.splice(index, 1);
              tabNumber--;
              $timeout(() => {
                vm.activeTab = 'conversion' + tabNumber;
              });
            }
          });
        },
        function () {}
      );
    };

    vm.startConversion = () => {
      if (vm.form.$invalid) {
        vm.form.$setSubmitted();
        return;
      }
      let conversions = vm.conversions.filter((a) => {
        return a.conversion !== null;
      });
      if (conversions.length > 0) {
        vm.conversions = conversions;
      }
      if (!angular.isUndefined(vm.flowOptions.purpose) && vm.flowOptions.purpose === '') {
        delete vm.flowOptions.purpose;
      }
      let data = angular.extend(vm.flowOptions, {
        actions: vm.conversions.map((x) => {
          let data = angular.copy(x.data);
          delete data.path;
          return {
            name: x.converter.name,
            options: data,
            path: x.data.path,
          };
        }),
      });
      const id = vm.baseUrl === 'workareas' ? vm.ip.workarea[0].id : vm.ip.id;
      const baseUrl = vm.baseUrl === 'workareas' ? 'workarea-entries' : vm.baseUrl;
      $http.post(appConfig.djangoUrl + baseUrl + '/' + id + '/actiontool/', data).then(() => {
        $rootScope.$broadcast('REFRESH_LIST_VIEW', {});
      });
    };
  }
}

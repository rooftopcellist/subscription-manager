pipeline {
  agent { label 'subman' }
  stages {
    // stage('prepare') {steps {echo 'prepare'}}
    stage('test') {
      parallel {
        stage('stylish') {
          agent { label 'subman-centos7' }
          steps { sh readFile(file: 'jenkins/stylish-tests.sh') }
        }
        stage('tito') {
          agent { label 'rpmbuild' }
          steps { sh readFile(file: 'jenkins/tito-tests.sh') }
        }
        stage('RHEL7 unit') {
          agent { label 'subman-centos7' }
          steps { sh readFile(file: 'jenkins/nose-tests.sh') }
        }
        stage('RHEL8 unit') {steps {echo 'nose'}}
        stage('Fedora unit') {
          steps { sh readFile(file: 'jenkins/python3-tests.sh') }
        }
        stage('opensuse42') {
          stages {
            stage('build') {
              steps {
                sh "scripts/suse_build.sh 'home:kahowell' 'openSUSE_Leap_42.2'"
                sh """
                if [ -d python-rhsm ]; then
                  cd python-rhsm
                  ../scripts/suse_build.sh 'home:kahowell' 'openSUSE_Leap_42.2' -k \$WORKSPACE
                  cd ..
                fi
                """
                sh readFile(file: 'jenkins/createrepo.sh')
              }
            }
            stage('nose') {steps { sh readFile(file: 'jenkins/suse-tests.sh') }}
          }
        }
        stage('sles11') {
          stages {
            stage('build') {
              steps {
                sh "scripts/suse_build.sh 'home:kahowell' 'SLE_11_SP4'"
                sh """
                if [ -d python-rhsm ]; then
                  cd python-rhsm
                  ../scripts/suse_build.sh 'home:kahowell' 'SLE_11_SP4' -k \$WORKSPACE
                  cd ..
                fi
                """
                sh readFile(file: 'jenkins/createrepo.sh')
              }
            }
            stage('nose') {steps { sh readFile(file: 'jenkins/suse-tests.sh') }}
          }
        }
        stage('sles12') {
          stages {
            stage('build') {
              steps {
                sh "scripts/suse_build.sh 'home:kahowell' 'SLE_12_SP1'"
                sh """
                if [ -d python-rhsm ]; then
                  cd python-rhsm
                  ../scripts/suse_build.sh 'home:kahowell' 'SLE_12_SP1' -k \$WORKSPACE
                  cd ..
                fi
                """
                sh readFile(file: 'jenkins/createrepo.sh')
              }
            }
            stage('nose') {steps { sh readFile(file: 'jenkins/suse-tests.sh') }}
          }
        }
        // TODO
        // stage('Functional') {
        //   stages{
        //     stage('Build RPM') {steps {echo 'Build RPM'}}
        //     stage('Prepare') {steps {echo 'Prepare'}}
        //     stage('Provision') {steps {echo 'Provisioning'}}
        //     stage('Tier 1') {steps {echo 'Tier 1'}}
        //   }
        // }
      }
    }
  // stage('cleanup') {steps {echo 'cleanup'}}
  }
}